"""
Data analysis utilities for basketball shot tracking.
"""

import statistics
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ShotStats:
    """Statistics for a set of shots."""
    total_shots: int
    makes: int
    misses: int
    unknowns: int
    make_percentage: float
    avg_confidence: float
    avg_duration: float
    consistency_score: float


class ShotAnalyzer:
    """Analyze basketball shot data for performance insights."""
    
    def __init__(self, shots_data: List[Dict]):
        """Initialize analyzer with shot data."""
        self.shots = shots_data
    
    def get_shot_stats(self) -> ShotStats:
        """Calculate overall statistics for shots."""
        if not self.shots:
            return ShotStats(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)
        
        results = [s.get('ball_tracking', {}).get('result', 'unknown') for s in self.shots]
        makes = len([r for r in results if r == 'made'])
        misses = len([r for r in results if r == 'missed'])
        unknowns = len([r for r in results if r == 'unknown'])
        
        make_pct = (makes / len(self.shots) * 100) if self.shots else 0.0
        
        confidences = [s.get('ball_tracking', {}).get('confidence', 0.0) for s in self.shots]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        durations = [s.get('detection_window', {}).get('duration', 0) for s in self.shots]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        consistency = self._calculate_consistency() if len(self.shots) > 1 else 1.0
        
        return ShotStats(
            total_shots=len(self.shots),
            makes=makes,
            misses=misses,
            unknowns=unknowns,
            make_percentage=make_pct,
            avg_confidence=avg_confidence,
            avg_duration=avg_duration,
            consistency_score=consistency,
        )
    
    def get_makes_vs_misses_analysis(self) -> Dict:
        """Compare form metrics between makes and misses."""
        makes = [s for s in self.shots if s.get('ball_tracking', {}).get('result') == 'made']
        misses = [s for s in self.shots if s.get('ball_tracking', {}).get('result') == 'missed']
        
        analysis = {
            'makes_count': len(makes),
            'misses_count': len(misses),
            'makes': self._extract_form_metrics(makes),
            'misses': self._extract_form_metrics(misses),
        }
        
        if makes and misses:
            analysis['differences'] = self._compare_metrics(
                analysis['makes'],
                analysis['misses']
            )
        
        return analysis
    
    def _extract_form_metrics(self, shots: List[Dict]) -> Dict:
        """Extract key form metrics from shots."""
        if not shots:
            return {}
        
        metrics = {
            'count': len(shots),
            'avg_elbow_angle_at_release': 0.0,
            'avg_duration': 0.0,
            'avg_confidence': 0.0,
        }
        
        elbow_angles = []
        durations = []
        confidences = []
        
        for shot in shots:
            form = shot.get('metrics', {})
            if 'angles' in form:
                elbow_angles.append(form['angles'].get('elbow', {}).get('at_release_deg', 0))
            
            durations.append(shot.get('detection_window', {}).get('duration', 0))
            confidences.append(shot.get('ball_tracking', {}).get('confidence', 0.0))
        
        if elbow_angles:
            metrics['avg_elbow_angle_at_release'] = sum(elbow_angles) / len(elbow_angles)
        if durations:
            metrics['avg_duration'] = sum(durations) / len(durations)
        if confidences:
            metrics['avg_confidence'] = sum(confidences) / len(confidences)
        
        return metrics
    
    def _compare_metrics(self, makes: Dict, misses: Dict) -> Dict:
        """Compare metrics between two groups."""
        return {
            'elbow_angle_difference': abs(
                makes.get('avg_elbow_angle_at_release', 0) - 
                misses.get('avg_elbow_angle_at_release', 0)
            ),
        }
    
    def _calculate_consistency(self) -> float:
        """Calculate shot consistency (0-1 scale)."""
        durations = [s.get('detection_window', {}).get('duration', 0) for s in self.shots]
        
        if len(durations) > 1:
            variance = statistics.variance(durations)
            consistency = max(0.0, 1.0 - (variance * 10))
            return min(1.0, consistency)
        
        return 0.5
    
    def get_improvement_suggestions(self) -> List[str]:
        """Generate coaching suggestions based on shot analysis."""
        suggestions = []
        stats = self.get_shot_stats()
        
        if stats.make_percentage < 50:
            suggestions.append(
                f"Current make rate is {stats.make_percentage:.1f}%. Focus on form consistency."
            )
        
        if stats.consistency_score < 0.6:
            suggestions.append(
                "Shot timing is inconsistent. Practice with the same release point each time."
            )
        
        comparison = self.get_makes_vs_misses_analysis()
        if comparison.get('differences'):
            diffs = comparison['differences']
            if diffs.get('elbow_angle_difference', 0) > 5:
                suggestions.append(
                    f"Elbow angle varies {diffs['elbow_angle_difference']:.1f}°. Keep it consistent."
                )
        
        if stats.avg_confidence < 0.6:
            suggestions.append(
                "Ensure clear camera view of your entire shot and the basket."
            )
        
        return suggestions or ["Continue practicing! Keep mechanics consistent."]


def generate_report(shots_data: List[Dict]) -> str:
    """Generate a comprehensive text report of shot analysis."""
    analyzer = ShotAnalyzer(shots_data)
    stats = analyzer.get_shot_stats()
    comparison = analyzer.get_makes_vs_misses_analysis()
    suggestions = analyzer.get_improvement_suggestions()
    
    report = f"""
======================================
    BASKETBALL SHOT ANALYSIS REPORT
======================================

OVERALL STATISTICS
------------------
Total Shots:              {stats.total_shots}
Makes:                    {stats.makes}
Misses:                   {stats.misses}
Unknown Results:          {stats.unknowns}
Make Percentage:          {stats.make_percentage:.1f}%
Consistency Score:        {stats.consistency_score:.2f} / 1.00
Avg Detection Confidence: {stats.avg_confidence:.2f}
Avg Shot Duration:        {stats.avg_duration:.2f}s

MAKES vs MISSES COMPARISON
---------------------------
Makes Count:    {comparison.get('makes_count')}
Misses Count:   {comparison.get('misses_count')}

IMPROVEMENT SUGGESTIONS
------------------------
"""
    
    for i, suggestion in enumerate(suggestions, 1):
        report += f"{i}. {suggestion}\n"
    
    report += "\n" + "=" * 40 + "\n"
    
    return report
