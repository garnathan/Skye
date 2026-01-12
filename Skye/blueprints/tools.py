"""
Tools API blueprint
Handles VRT calculator for vehicle imports
"""
from flask import Blueprint, jsonify, request, current_app
import requests

tools_bp = Blueprint('tools', __name__)


@tools_bp.route('/api/vrt-calculate', methods=['POST'])
def vrt_calculate():
    """Calculate VRT for vehicle import to Ireland"""
    try:
        from datetime import datetime

        data = request.get_json()

        uk_price = float(data.get('uk_price', 0))
        co2_emissions = int(data.get('co2_emissions', 0))
        fuel_type = data.get('fuel_type', 'petrol')
        vehicle_age = int(data.get('vehicle_age', 0))
        transport_method = data.get('transport_method', 'ferry')
        import_origin = data.get('import_origin', 'uk')

        if uk_price <= 0 or co2_emissions <= 0:
            return jsonify({'error': 'Invalid input values'}), 400

        # Get current GBP to EUR exchange rate
        try:
            rate_response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/GBP',
                timeout=10
            )
            if rate_response.status_code == 200:
                exchange_rate = rate_response.json()['rates'].get('EUR', 1.17)
            else:
                exchange_rate = 1.17
        except:
            exchange_rate = 1.17

        # Convert UK price to EUR
        vehicle_value_eur = uk_price * exchange_rate

        # Transport costs
        transport_cost = 300 if transport_method == 'ferry' else 150
        insurance_cost = vehicle_value_eur * 0.015
        customs_clearance = 50
        total_transport = transport_cost + insurance_cost + customs_clearance

        # OMV (Open Market Value)
        omv = vehicle_value_eur + total_transport

        # Customs Duty
        customs_duty = vehicle_value_eur * 0.10 if import_origin == 'uk' else 0.0

        # VRT calculation based on CO2 emissions
        co2_bands = [
            (0, 50, 7, 140), (51, 80, 9, 180), (81, 85, 9.75, 195),
            (86, 90, 10.5, 210), (91, 95, 11.25, 225), (96, 100, 12, 240),
            (101, 105, 12.75, 255), (106, 110, 13.5, 270),
            (111, 115, 15.25, 305),
            (116, 120, 16, 320), (121, 125, 16.75, 335),
            (126, 130, 17.5, 350),
            (131, 135, 19.25, 385), (136, 140, 20, 400),
            (141, 145, 21.5, 430),
            (146, 150, 25, 500), (151, 155, 27.5, 550),
            (156, 170, 30, 600),
            (171, 190, 35, 700), (191, float('inf'), 41, 820)
        ]

        # Find VRT rate and minimum
        co2_rate, vrt_minimum = 41, 820  # Default to highest
        for min_co2, max_co2, rate, minimum in co2_bands:
            if min_co2 <= co2_emissions <= max_co2:
                co2_rate, vrt_minimum = rate, minimum
                break

        # Calculate VRT
        base_vrt = omv * (co2_rate / 100)

        # Apply age depreciation
        if vehicle_age > 0:
            depreciation_rate = min(vehicle_age * 0.02, 0.1)
            base_vrt = base_vrt * (1 - depreciation_rate)

        final_vrt = max(base_vrt, vrt_minimum)

        # VAT calculation
        vat_base = vehicle_value_eur + customs_duty + final_vrt
        vat_amount = vat_base * 0.21

        # Total cost
        registration_fee = 102
        total_import_cost = (
            vehicle_value_eur + total_transport + customs_duty +
            final_vrt + vat_amount + registration_fee
        )

        current_app.logger.info(
            f"VRT calculated: {uk_price} GBP = {total_import_cost:.2f} EUR"
        )

        return jsonify({
            'purchase_details': {
                'uk_price_gbp': uk_price,
                'exchange_rate': round(exchange_rate, 4),
                'vehicle_value_eur': round(vehicle_value_eur, 2),
                'import_origin': import_origin.upper()
            },
            'transport_costs': {
                'transport': transport_cost,
                'insurance': round(insurance_cost, 2),
                'customs_clearance': customs_clearance,
                'total': round(total_transport, 2)
            },
            'omv': round(omv, 2),
            'customs_duty': round(customs_duty, 2),
            'customs_duty_applicable': import_origin == 'uk',
            'vrt_calculation': {
                'co2_emissions': co2_emissions,
                'co2_rate_percent': co2_rate,
                'base_vrt': round(base_vrt, 2),
                'minimum_vrt': vrt_minimum,
                'final_vrt': round(final_vrt, 2)
            },
            'vat_calculation': {
                'vat_base': round(vat_base, 2),
                'vat_rate_percent': 21,
                'vat_amount': round(vat_amount, 2)
            },
            'additional_costs': {
                'registration_fee': registration_fee
            },
            'total_import_cost': round(total_import_cost, 2)
        })

    except Exception as e:
        current_app.logger.error(f"VRT calculation error: {str(e)}")
        return jsonify({'error': str(e)}), 500
