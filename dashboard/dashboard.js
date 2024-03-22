let currentPrices = {};

$(document).ready(function() {
    $('#pairSelect').select2({ placeholder: "Select a pair", width: 'resolve' });
    fetchAndPopulatePairs();

    $('#pairSelect').on('select2:select', async function(e) {
        const selectedSymbol = e.params.data.id;
        // Ensure currentPrices is updated before allowing addition
        await fetchCurrentPrice(selectedSymbol);
    });

    document.getElementById('addPair').addEventListener('click', async function() {
        const symbol = $('#pairSelect').val();
        const targetPrice = parseFloat(document.getElementById('targetPrice').value);
        const initialInvestment = parseFloat(document.getElementById('initialInvestment').value);
        
        // Make sure to fetch and wait for the current price if not already done
        if (!currentPrices[symbol]) {
            await fetchCurrentPrice(symbol);
        }

        // Now, proceed assuming the current price is available
        if (!isNaN(targetPrice) && !isNaN(initialInvestment) && symbol && currentPrices[symbol]) {
            // Use the current price from currentPrices object
            addPriceTile(symbol, targetPrice, initialInvestment, currentPrices[symbol]);
            connectToBinanceWS(symbol, currentPrices[symbol]);
            document.getElementById('targetPrice').value = '';
            document.getElementById('initialInvestment').value = '';
        } else {
            alert("Please select a pair, enter a valid target price, and initial investment.");
        }
    });
});


async function fetchAndPopulatePairs() {
    const url = "https://api.binance.com/api/v3/exchangeInfo";
    try {
        const response = await fetch(url);
        const data = await response.json();
        const selectElement = $('#pairSelect');
        data.symbols.filter(symbol => symbol.status === "TRADING").forEach(symbol => {
            selectElement.append(new Option(symbol.symbol, symbol.symbol));
        });
    } catch (error) {
        console.error("Failed to fetch pairs: ", error);
    }
}

async function fetchCurrentPrice(symbol) {
    const url = `https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        currentPrices[symbol] = parseFloat(data.price).toFixed(5);
        displayCurrentPrice(symbol, currentPrices[symbol]);
    } catch (error) {
        console.error("Failed to fetch current price: ", error);
    }
}

function displayCurrentPrice(symbol, price) {
    const currentPriceDisplay = document.getElementById('currentPriceDisplay') || createCurrentPriceDisplay();
    currentPriceDisplay.innerHTML = `Current Price of ${symbol}: $<strong>${price}</strong>`;
}

function createCurrentPriceDisplay() {
    const container = document.getElementById('addPairContainer');
    const priceDisplay = document.createElement('div');
    priceDisplay.id = 'currentPriceDisplay';
    container.insertBefore(priceDisplay, container.firstChild);
    return priceDisplay;
}

function addPriceTile(symbol, targetPrice, initialInvestment, initialPrice) {
    const tile = document.createElement('div');
    tile.classList.add('price-tile');
    tile.id = `tile-${symbol}`;

    tile.innerHTML = `
        <div><strong>${symbol}</strong></div>
        <div>Initial Price: $<span id="initial-${symbol}">${initialPrice}</span></div>
        <div>Current Price: $<span id="price-${symbol}">${initialPrice}</span></div>
        <div>Change: <span id="change-${symbol}" style="color: black;">0%</span></div>
        <div>Target Price: $<span id="target-${symbol}">${targetPrice}</span></div>
        <div>Gain/Loss: $<span id="gainLoss-${symbol}">0.00</span></div>
    `;

    // Add event listener for showing chart modal on click
    tile.addEventListener('click', () => {
        fetchChartData(symbol).then(data => {
            displayChart(symbol, data);
        });
        showModal();
    });

    document.getElementById('pricesContainer').appendChild(tile);

    // Store additional data attributes for gain/loss calculations
    tile.setAttribute('data-initial-price', initialPrice);
    tile.setAttribute('data-initial-investment', initialInvestment);
	
	
}

function connectToBinanceWS(symbol, initialPrice) {
    const ws = new WebSocket(`wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@trade`);
    ws.onmessage = function(event) {
        const trade = JSON.parse(event.data);
        const currentPrice = parseFloat(trade.p).toFixed(5);
        updateTile(symbol, currentPrice);
    };
}

function updateTile(symbol, currentPrice) {
    const tile = document.getElementById(`tile-${symbol}`);
    if (!tile) return; // Safety check

    const initialPrice = parseFloat(tile.getAttribute('data-initial-price'));
    const initialInvestment = parseFloat(tile.getAttribute('data-initial-investment'));
    
    // Ensure initial values are valid
    if (isNaN(initialPrice) || isNaN(initialInvestment)) {
        console.error("Invalid initial price or investment for symbol:", symbol);
        return;
    }

    const currentPriceElement = document.getElementById(`price-${symbol}`);
    const gainLossElement = document.getElementById(`gainLoss-${symbol}`);

    // Calculate the price change and the gain/loss
    const priceChange = ((currentPrice - initialPrice) / initialPrice) * 100;
    const gainLoss = ((currentPrice - initialPrice) * initialInvestment).toFixed(2);

    // Update the UI elements with the new values
    if (currentPriceElement && gainLossElement) {
        currentPriceElement.textContent = `$${currentPrice}`;
        document.getElementById(`change-${symbol}`).textContent = `${priceChange.toFixed(2)}%`;
        document.getElementById(`change-${symbol}`).style.color = priceChange >= 0 ? 'green' : 'red';
        gainLossElement.textContent = `$${gainLoss}`;
        gainLossElement.style.color = parseFloat(gainLoss) >= 0 ? 'green' : 'red';
    }
}


async function fetchChartData(symbol) {
    const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1d&limit=7`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data.map(kline => ({
            t: new Date(kline[0]),
            y: parseFloat(kline[4])
        }));
    } catch (error) {
        console.error("Failed to fetch chart data: ", error);
    }
}

function displayChart(symbol, chartData) {
    const modal = document.getElementById('chartModal');
    const ctx = modal.querySelector('#chartCanvas').getContext('2d');
    if (window.myChart instanceof Chart) {
        window.myChart.destroy();
    }
    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: `${symbol} Last 7 Days`,
                data: chartData,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                            day: 'MM/DD/YYYY'
                        }
                    }
                },
                y: {
                    beginAtZero: false
                }
            }
        }
    });
    showModal();
}

function showModal() {
    document.getElementById('chartModal').style.display = 'block';
}

function hideModal() {
    document.getElementById('chartModal').style.display = 'none';
}

// Close modal when the 'x' is clicked
document.querySelector('.close').addEventListener('click', hideModal);
