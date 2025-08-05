from django.core.cache import cache
from django.db import models
from django.db.models import Count, Q, F, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Optional, Tuple
import logging

from match_history.models import ChampionStatsPatch, Champion, Match, Participant

logger = logging.getLogger(__name__)


class ChampionStatsManager:
    """
    Manager class for handling champion statistics calculations and caching.
    Provides efficient database queries and caching for performance optimization.
    """
    
    # Cache configuration
    CACHE_TIMEOUT = 3600  # 1 hour
    CACHE_PREFIX = 'champion_stats'
    PATCH_STATS_CACHE_KEY = f'{CACHE_PREFIX}_patch_{{patch}}'
    ALL_STATS_CACHE_KEY = f'{CACHE_PREFIX}_all'
    CHAMPION_STATS_CACHE_KEY = f'{CACHE_PREFIX}_champion_{{champion_id}}_{{patch}}'
    
    def __init__(self):
        self.cache_timeout = self.CACHE_TIMEOUT
    
    def get_champion_patch_stats(self, patch: str = None, champion_id: str = None, 
                                use_cache: bool = True) -> Dict:
        """
        Retrieve and organize champion statistics with efficient database queries.
        
        Args:
            patch: Specific patch version to filter by
            champion_id: Specific champion ID to filter by  
            use_cache: Whether to use caching (default: True)
            
        Returns:
            Dictionary containing champion statistics data
        """
        # Generate cache key based on parameters
        if champion_id and patch:
            cache_key = self.CHAMPION_STATS_CACHE_KEY.format(
                champion_id=champion_id, patch=patch
            )
        elif patch:
            cache_key = self.PATCH_STATS_CACHE_KEY.format(patch=patch)
        else:
            cache_key = self.ALL_STATS_CACHE_KEY
            
        # Try to get from cache first
        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_data
        
        # Build query with optimizations
        queryset = ChampionStatsPatch.objects.select_related('champion')
        
        if patch:
            queryset = queryset.filter(patch=patch)
        if champion_id:
            queryset = queryset.filter(champion__champion_id=champion_id)
            
        # Execute optimized query
        stats_data = self._execute_stats_query(queryset, patch)
        
        # Cache the results
        if use_cache:
            cache.set(cache_key, stats_data, self.cache_timeout)
            logger.info(f"Cached data for key: {cache_key}")
            
        return stats_data
    
    def _execute_stats_query(self, queryset, patch: str = None) -> Dict:
        """
        Execute the optimized database query for champion statistics.
        
        Args:
            queryset: Pre-filtered ChampionStatsPatch queryset
            patch: Patch version for additional calculations
            
        Returns:
            Dictionary with organized statistics data
        """
        start_time = timezone.now()
        
        # Get total matches for the patch if specified
        total_matches_in_patch = None
        if patch:
            total_matches_in_patch = self._get_total_matches_for_patch(patch)
        
        # Execute main query with aggregations
        stats_list = list(queryset.values(
            'champion__champion_id',
            'champion__name', 
            'champion__image_path',
            'patch',
            'total_played',
            'total_wins',
            'total_losses',
            'total_bans',
            'win_rate',
            'pick_rate', 
            'ban_rate',
            'last_updated'
        ).order_by('-total_played', '-win_rate'))
        
        # Recalculate rates if we have total matches data
        if total_matches_in_patch:
            for stat in stats_list:
                if stat['total_played'] > 0:
                    stat['win_rate'] = round((stat['total_wins'] / stat['total_played']) * 100, 2)
                    stat['pick_rate'] = round((stat['total_played'] / total_matches_in_patch) * 100, 2)
                    stat['ban_rate'] = round((stat['total_bans'] / total_matches_in_patch) * 100, 2)
        
        # Calculate query performance
        query_time = (timezone.now() - start_time).total_seconds() * 1000
        logger.info(f"Champion stats query executed in {query_time:.2f}ms")
        
        # Organize response data
        response_data = {
            'statistics': stats_list,
            'metadata': {
                'total_champions': len(stats_list),
                'patch': patch,
                'total_matches_in_patch': total_matches_in_patch,
                'query_time_ms': round(query_time, 2),
                'last_updated': timezone.now().isoformat(),
                'cache_timeout': self.cache_timeout
            }
        }
        
        return response_data
    
    def _get_total_matches_for_patch(self, patch: str) -> int:
        """
        Get total number of matches for a specific patch.
        Uses caching for performance.
        
        Args:
            patch: Patch version string
            
        Returns:
            Total number of matches in the patch
        """
        cache_key = f'{self.CACHE_PREFIX}_total_matches_{patch}'
        
        # Try cache first
        total_matches = cache.get(cache_key)
        if total_matches is not None:
            return total_matches
            
        # Query database
        total_matches = Match.objects.filter(
            game_version__startswith=patch
        ).count()
        
        # Cache for longer since this changes less frequently
        cache.set(cache_key, total_matches, self.cache_timeout * 2)
        
        return total_matches
    
    def update_champion_stats_bulk(self, patch: str, recalculate_rates: bool = True) -> Dict:
        """
        Bulk update champion statistics for a specific patch.
        Optimized for performance with batch operations.
        
        Args:
            patch: Patch version to update
            recalculate_rates: Whether to recalculate all rate fields
            
        Returns:
            Dictionary with update results
        """
        start_time = timezone.now()
        
        # Get total matches for rate calculations
        total_matches = self._get_total_matches_for_patch(patch)
        
        # Get all champion stats for the patch
        champion_stats = ChampionStatsPatch.objects.filter(patch=patch)
        
        updated_count = 0
        if recalculate_rates:
            # Bulk update calculated fields
            for stat in champion_stats:
                stat.update_calculated_fields(total_matches)
                updated_count += 1
            
            # Bulk update to database
            ChampionStatsPatch.objects.bulk_update(
                champion_stats, 
                ['win_rate', 'pick_rate', 'ban_rate', 'last_updated'],
                batch_size=100
            )
        
        # Invalidate related caches
        self.invalidate_patch_cache(patch)
        
        update_time = (timezone.now() - start_time).total_seconds() * 1000
        
        return {
            'updated_champions': updated_count,
            'patch': patch,
            'total_matches': total_matches,
            'update_time_ms': round(update_time, 2)
        }
    
    def get_top_champions_by_metric(self, patch: str, metric: str = 'win_rate', 
                                   limit: int = 10, use_cache: bool = True) -> List[Dict]:
        """
        Get top champions by a specific metric (win_rate, pick_rate, ban_rate).
        
        Args:
            patch: Patch version
            metric: Metric to sort by ('win_rate', 'pick_rate', 'ban_rate')
            limit: Number of champions to return
            use_cache: Whether to use caching
            
        Returns:
            List of champion statistics dictionaries
        """
        cache_key = f'{self.CACHE_PREFIX}_top_{metric}_{patch}_{limit}'
        
        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        # Validate metric
        valid_metrics = ['win_rate', 'pick_rate', 'ban_rate', 'total_played']
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric: {metric}. Must be one of {valid_metrics}")
        
        # Query top champions
        queryset = ChampionStatsPatch.objects.filter(
            patch=patch,
            total_played__gt=0  # Only include champions that have been played
        ).select_related('champion').order_by(f'-{metric}')[:limit]
        
        top_champions = list(queryset.values(
            'champion__champion_id',
            'champion__name',
            'champion__image_path', 
            'total_played',
            'win_rate',
            'pick_rate',
            'ban_rate'
        ))
        
        if use_cache:
            cache.set(cache_key, top_champions, self.cache_timeout)
            
        return top_champions
    
    def get_champion_performance_trends(self, champion_id: str, 
                                      patches: List[str] = None) -> Dict:
        """
        Get performance trends for a specific champion across patches.
        
        Args:
            champion_id: Champion ID to analyze
            patches: List of patches to include (if None, gets recent patches)
            
        Returns:
            Dictionary with trend data
        """
        cache_key = f'{self.CACHE_PREFIX}_trends_{champion_id}'
        
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Get recent patches if not specified
        if patches is None:
            patches = list(ChampionStatsPatch.objects.filter(
                champion__champion_id=champion_id
            ).values_list('patch', flat=True).distinct().order_by('-patch')[:5])
        
        # Get stats for each patch
        trend_data = []
        for patch in patches:
            try:
                stat = ChampionStatsPatch.objects.get(
                    champion__champion_id=champion_id,
                    patch=patch
                )
                trend_data.append({
                    'patch': patch,
                    'win_rate': stat.win_rate,
                    'pick_rate': stat.pick_rate,
                    'ban_rate': stat.ban_rate,
                    'total_played': stat.total_played
                })
            except ChampionStatsPatch.DoesNotExist:
                continue
        
        result = {
            'champion_id': champion_id,
            'trends': trend_data,
            'patches_analyzed': len(trend_data)
        }
        
        cache.set(cache_key, result, self.cache_timeout)
        return result
    
    def invalidate_cache(self, cache_key: str = None):
        """
        Invalidate specific cache key or all champion stats caches.
        
        Args:
            cache_key: Specific cache key to invalidate (if None, clears all)
        """
        if cache_key:
            cache.delete(cache_key)
            logger.info(f"Invalidated cache key: {cache_key}")
        else:
            # Clear all champion stats caches
            # Note: This is a simplified approach. In production, you might want
            # to use cache versioning or maintain a list of active cache keys
            cache.delete_many([
                self.ALL_STATS_CACHE_KEY,
            ])
            logger.info("Invalidated all champion stats caches")
    
    def invalidate_patch_cache(self, patch: str):
        """
        Invalidate all caches related to a specific patch.
        
        Args:
            patch: Patch version to invalidate caches for
        """
        cache_keys_to_delete = [
            self.PATCH_STATS_CACHE_KEY.format(patch=patch),
            f'{self.CACHE_PREFIX}_total_matches_{patch}',
            f'{self.CACHE_PREFIX}_top_win_rate_{patch}_10',
            f'{self.CACHE_PREFIX}_top_pick_rate_{patch}_10',
            f'{self.CACHE_PREFIX}_top_ban_rate_{patch}_10',
        ]
        
        cache.delete_many(cache_keys_to_delete)
        logger.info(f"Invalidated patch caches for: {patch}")
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache performance statistics.
        Note: This is a simplified version. In production, you'd want more
        sophisticated cache monitoring.
        
        Returns:
            Dictionary with cache statistics
        """
        # This would require cache backend that supports statistics
        # For now, return basic info
        return {
            'cache_timeout': self.cache_timeout,
            'cache_prefix': self.CACHE_PREFIX,
            'available': cache._cache is not None if hasattr(cache, '_cache') else True
        }