def get_content():
    return {
        'html': '''
        <div class="vrt-calculator-page">
            <div class="vrt-header">
                <h1>🇮🇪 Ireland VRT Calculator</h1>
                <p>Calculate Vehicle Registration Tax for importing cars to Ireland</p>
                <button onclick="window.history.back()" class="back-button">← Back to Tools</button>
            </div>

            <div class="vrt-form-container">
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Important:</strong> This calculator provides estimates only. Always verify current VRT rates with Irish Revenue.
                </div>
                
                <form id="vrtForm" class="vrt-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="ukPrice">UK Purchase Price (£)</label>
                            <input type="number" id="ukPrice" name="uk_price" step="0.01" min="0" required>
                        </div>

                        <div class="form-group">
                            <label for="co2Emissions">CO2 Emissions (g/km)</label>
                            <input type="number" id="co2Emissions" name="co2_emissions" min="0" required>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="fuelType">Fuel Type</label>
                            <select id="fuelType" name="fuel_type" required>
                                <option value="petrol">Petrol</option>
                                <option value="diesel">Diesel</option>
                                <option value="electric">Electric</option>
                                <option value="hybrid">Hybrid</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="vehicleAge">Vehicle Age (years)</label>
                            <input type="number" id="vehicleAge" name="vehicle_age" min="0" value="0">
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="importOrigin">Import Origin</label>
                            <select id="importOrigin" name="import_origin" required>
                                <option value="uk">Great Britain (10% customs duty)</option>
                                <option value="ni">Northern Ireland (0% customs duty)</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="transportMethod">Transport Method</label>
                            <select id="transportMethod" name="transport_method" required>
                                <option value="ferry">Ferry (€300)</option>
                                <option value="drive">Drive (€150)</option>
                            </select>
                        </div>
                    </div>

                    <button type="submit" class="calculate-btn">Calculate VRT</button>
                </form>
            </div>

            <div id="vrtResults" class="vrt-results" style="display: none;">
                <h2>VRT Calculation Results</h2>
                <div id="resultsContent"></div>
            </div>
        </div>

        <style>
        .vrt-calculator-page {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .vrt-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .vrt-header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .back-button {
            background: #6c757d;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 15px;
        }

        .back-button:hover {
            background: #5a6268;
        }

        .vrt-form-container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .alert {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            color: #856404;
        }

        .vrt-form {
            display: grid;
            gap: 20px;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #2c3e50;
        }

        .form-group input,
        .form-group select {
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #3498db;
        }

        .calculate-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .calculate-btn:hover {
            transform: translateY(-2px);
        }

        .vrt-results {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .result-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }

        .result-card h4 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }

        .result-value {
            font-size: 24px;
            font-weight: bold;
            color: #27ae60;
        }

        .total-cost {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }

        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
        }
        </style>

        <script>
        document.getElementById('vrtForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/api/vrt-calculate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    throw new Error('Calculation failed');
                }
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                alert('Error calculating VRT: ' + error.message);
            }
        });

        function displayResults(result) {
            const resultsDiv = document.getElementById('vrtResults');
            const contentDiv = document.getElementById('resultsContent');
            
            contentDiv.innerHTML = `
                <div class="results-grid">
                    <div class="result-card">
                        <h4>Purchase Price</h4>
                        <div class="result-value">£${result.purchase_details.uk_price_gbp.toLocaleString()}</div>
                        <small>€${result.purchase_details.vehicle_value_eur.toLocaleString()} (Rate: ${result.purchase_details.exchange_rate})</small>
                    </div>
                    
                    <div class="result-card">
                        <h4>Transport Costs</h4>
                        <div class="result-value">€${result.transport_costs.total.toLocaleString()}</div>
                    </div>
                    
                    <div class="result-card">
                        <h4>Customs Duty</h4>
                        <div class="result-value">€${result.customs_duty.toLocaleString()}</div>
                        <small>${result.customs_duty_applicable ? '10% (Great Britain)' : '0% (Northern Ireland)'}</small>
                    </div>
                    
                    <div class="result-card">
                        <h4>VRT</h4>
                        <div class="result-value">€${result.vrt_calculation.final_vrt.toLocaleString()}</div>
                        <small>${result.vrt_calculation.co2_rate_percent}% rate (${result.vrt_calculation.co2_emissions}g CO2/km)</small>
                    </div>
                    
                    <div class="result-card">
                        <h4>VAT (21%)</h4>
                        <div class="result-value">€${result.vat_calculation.vat_amount.toLocaleString()}</div>
                    </div>
                    
                    <div class="result-card">
                        <h4>Registration Fee</h4>
                        <div class="result-value">€${result.additional_costs.registration_fee}</div>
                    </div>
                </div>
                
                <div class="total-cost">
                    <h3>Total Import Cost</h3>
                    <div style="font-size: 32px; font-weight: bold;">€${result.total_import_cost.toLocaleString()}</div>
                </div>
            `;
            
            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
        </script>
        '''
    }