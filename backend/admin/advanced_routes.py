from flask import Blueprint, request, jsonify
from admin.advanced_analytics import advanced_analytics
from auth.utils import admin_required  # CORRECTED IMPORT

advanced_analytics_bp = Blueprint('advanced_analytics', __name__)

@advanced_analytics_bp.route('/trends', methods=['GET'])
@admin_required
def get_trend_analysis(current_user):
    """Get trend analysis"""
    try:
        days = request.args.get('days', 90, type=int)
        trends = advanced_analytics.get_trend_analysis(days)
        return jsonify(trends), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@advanced_analytics_bp.route('/heatmap', methods=['GET'])
@admin_required
def get_geospatial_heatmap(current_user):
    """Get geospatial heatmap data"""
    try:
        heatmap = advanced_analytics.get_geospatial_heatmap()
        return jsonify(heatmap), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@advanced_analytics_bp.route('/predictive-insights', methods=['GET'])
@admin_required
def get_predictive_insights(current_user):
    """Get predictive insights"""
    try:
        insights = advanced_analytics.get_predictive_insights()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@advanced_analytics_bp.route('/performance', methods=['GET'])
@admin_required
def get_performance_metrics(current_user):
    """Get comprehensive performance metrics"""
    try:
        metrics = advanced_analytics.get_performance_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@advanced_analytics_bp.route('/patrol-recommendations', methods=['GET'])
@admin_required
def get_patrol_recommendations(current_user):
    """Get patrol recommendations"""
    try:
        recommendations = advanced_analytics.generate_patrol_recommendations()
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@advanced_analytics_bp.route('/high-risk-areas', methods=['GET'])
@admin_required
def get_high_risk_areas(current_user):
    """Get high risk areas"""
    try:
        risk_areas = advanced_analytics.get_high_risk_areas()
        return jsonify(risk_areas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500