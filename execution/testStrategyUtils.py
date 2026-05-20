#!/usr/bin/env python3
"""
Test Social Media Strategy Utilities

Test the new utility functions for growth strategy.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils import (
    calculateEngagementRate,
    optimizePostingSchedule,
    generateHashtagStrategy,
    analyzeContentPerformance,
    createGrowthProjection,
    generateContentCalendar
)

def testEngagementRate():
    """Test engagement rate calculation."""
    print("🧪 Testing calculateEngagementRate...")

    # Test normal case
    rate = calculateEngagementRate(likes=100, comments=20, shares=10, reach=1000)
    assert rate == 13.0, f"Expected 13.0, got {rate}"
    print("✅ Normal case: PASS")

    # Test zero reach
    rate = calculateEngagementRate(likes=10, comments=5, shares=2, reach=0)
    assert rate == 0.0, f"Expected 0.0, got {rate}"
    print("✅ Zero reach case: PASS")

def testPostingSchedule():
    """Test posting schedule optimization."""
    print("\n🧪 Testing optimizePostingSchedule...")

    mockData = [
        {'hour': 9, 'engagement': 150},
        {'hour': 9, 'engagement': 200},
        {'hour': 14, 'engagement': 300},
        {'hour': 14, 'engagement': 250},
        {'hour': 19, 'engagement': 400},
        {'hour': 19, 'engagement': 350},
        {'hour': 22, 'engagement': 100}
    ]

    result = optimizePostingSchedule(mockData)

    assert 19 in result['optimal_hours'], "19h should be optimal"
    assert 14 in result['optimal_hours'], "14h should be optimal"
    print("✅ Optimal hours identified: PASS")

def testHashtagStrategy():
    """Test hashtag generation."""
    print("\n🧪 Testing generateHashtagStrategy...")

    strategy = generateHashtagStrategy('empreendedorismo_tech', 'instagram')

    assert '#Empreendedorismo' in strategy['primary'], "Primary hashtag missing"
    assert len(strategy['primary']) == 2, "Should have 2 primary hashtags"
    assert strategy['max_recommended'] == 8, "Instagram should allow 8 hashtags"
    print("✅ Hashtag strategy generated: PASS")

def testContentAnalysis():
    """Test content performance analysis."""
    print("\n🧪 Testing analyzeContentPerformance...")

    mockPosts = [
        {'type': 'reel', 'engagement_rate': 5.2},
        {'type': 'reel', 'engagement_rate': 4.8},
        {'type': 'static', 'engagement_rate': 2.1},
        {'type': 'static', 'engagement_rate': 1.9},
        {'type': 'carousel', 'engagement_rate': 3.5}
    ]

    analysis = analyzeContentPerformance(mockPosts)

    assert analysis['best_content_type'] == 'reel', "Reels should be best performing"
    assert analysis['total_posts_analyzed'] == 5, "Should analyze all posts"
    print("✅ Content analysis: PASS")

def testGrowthProjection():
    """Test growth projection."""
    print("\n🧪 Testing createGrowthProjection...")

    projection = createGrowthProjection(
        currentFollowers=4500,
        targetFollowers=10000,
        days=30
    )

    assert projection['feasibility'] in ['realistic', 'challenging', 'ambitious'], "Should classify feasibility"
    assert len(projection['projection']) == 30, "Should have 30 days of projection"
    assert projection['projection'][-1]['projected_followers'] >= 10000, "Should reach target"
    print("✅ Growth projection: PASS")

def testContentCalendar():
    """Test content calendar generation."""
    print("\n🧪 Testing generateContentCalendar...")

    calendar = generateContentCalendar('bastidores_jornada', 5)

    assert len(calendar) == 5, "Should generate 5 days"
    assert calendar[0]['theme'] == 'bastidores_jornada', "Theme should match"
    assert 'content_idea' in calendar[0], "Should have content idea"
    print("✅ Content calendar: PASS")

def main():
    """Run all tests."""
    print("🚀 Testing Social Media Strategy Utilities\n")

    try:
        testEngagementRate()
        testPostingSchedule()
        testHashtagStrategy()
        testContentAnalysis()
        testGrowthProjection()
        testContentCalendar()

        print("\n🎉 All tests passed! Strategy utilities are working correctly.")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())