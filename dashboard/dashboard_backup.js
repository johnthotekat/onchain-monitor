
let currentPrices = {};

$(document).ready(function() {
  $('#pairSelect').select2({ placeholder: "Select a pair", width: 'resolve' });
  fetchAndPopulatePairs().catch(error => console.error("Failed to fetch pairs:", error)); // Handle errors during pair fetching

  $('#pairSelect').on('select2:select', async function(e) {
    const selectedSymbol = e.params.data.id;
    await fetchCurrentPrice(selectedSymbol);
  });

  document.getElementById('addPair').addEventListener('click', function() {
    const symbol = $('#pairSelect').val();
    const targetPrice = parseFloat(document.getElementById('targetPrice').value);
    const initialInvestment = parseFloat(document.getElementById('initialInvestment').value); // Assuming you have an input for initial investment
    if (!isNaN(targetPrice) && symbol && currentPrices[symbol]) {
      addPriceTile(symbol, targetPrice, initialInvestment);
      connectToBinanceWS(symbol, currentPrices[symbol]);
      document.getElementById('targetPrice').value = ''; // Clear the target price input after adding
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

        data.symbols.forEach(symbol => {
            if (symbol.status === "TRADING") {
                selectElement.append(new Option(symbol.symbol, symbol.symbol));
            }
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
        const currentPrice = parseFloat(data.price).toFixed(5);
        currentPrices[symbol] = currentPrice;
        displayCurrentPrice(symbol, currentPrice);
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

let currentPrices = {};

$(document).ready(function() {
  $('#pairSelect').select2({ placeholder: "Select a pair", width: 'resolve' });
  fetchAndPopulatePairs();

  $('#pairSelect').on('select2:select', async function(e) {
    const selectedSymbol = e.params.data.id;
    await fetchCurrentPrice(selectedSymbol);
  });

  document.getElementById('addPair').addEventListener('click', function() {
    const symbol = $('#pairSelect').val();
    const targetPrice = parseFloat(document.getElementById('targetPrice').value);
    const initialInvestment = parseFloat(document.getElementById('initialInvestment').value); // Assuming you have an input for initial investment
    if (!isNaN(targetPrice) && symbol && currentPrices[symbol]) {
      addPriceTile(symbol, targetPrice, initialInvestment);
      connectToBinanceWS(symbol, currentPrices[symbol]);
      document.getElementById('targetPrice').value = ''; // Clear the target price input after adding
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

    data.symbols.forEach(symbol => {
      if (symbol.status === "TRADING") {
        selectElement.append(new Option(symbol.symbol, symbol.symbol));
      }
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
    const currentPrice = parseFloat(data.price).toFixed(2);
    currentPrices[symbol] = currentPrice;
    displayCurrentPrice(symbol, currentPrice);
  } catch (error) {
    console.error("Failed to fetch current price: ", error);
  }
}

function displayCurrentPrice(symbol, price) {
  const currentPriceDisplay = document.getElementById('currentPriceDisplay') || createCurrentPriceDisplay();
  currentPriceDisplay.innerHTML = `Current Price of ${symbol}: <span class="math-inline"><strong\></span>{price}</strong>`;
}

function createCurrentPriceDisplay() {
  const container = document.getElementById('addPairContainer');
  const priceDisplay = document.createElement('div');
  priceDisplay.id = 'currentPriceDisplay';
  container.insertBefore(priceDisplay, container.firstChild);
  return priceDisplay;
}

function addPriceTile(symbol, targetPrice, initialInvestment) {
  const tile = document.createElement('div');
  tile.classList.add('price-tile');
  tile.id = `tile-${symbol}`;

  const initialPrice = currentPrices[symbol]; // Assuming price is already fetched

  const initialTotalValue = initialInvestment * initialPrice;

  const tileData = {
    symbol,
    initialPrice,
    targetPrice,
    initialTotalValue,
    initialInvestment,
  };

  tile.innerHTML = `
    <div><strong>${symbol}</strong></div>
    <div>Initial Price: <span class="math-inline"><span id\="initial\-</span>{symbol}">${initialPrice}</span></div>
    <div>Current Price: <span class="math-inline"><span id\="price\-</span>{symbol}"><span class="math-inline">\{initialPrice\}</span\></div\>
<div\>Change\: <span id\="change\-</span>{symbol}" style="color: black;">0%</span></div>
    <div>Target Price: <span class="math-inline"><span id\="target\-</span>{symbol}">${targetPrice}</span></div>
    <div>Gain/Loss: <span class="math-inline"><span id\="gainLoss\-</span>{symbol}">0.00</span></div>
  `;

  // Add click event listener to tile
  tile.addEventListener('click', () => {
    fetchChartData(symbol).then(data => {
      displayChart(symbol, data);
    });
    showModal();
  });

  document.getElementById('pricesContainer').appendChild(tile);
  updateTile(symbol, initialPrice, 0); // Update tile initially with fetched price


function connectToBinanceWS(symbol, initialPrice) {
    const ws = new WebSocket(`wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@trade`);
    ws.onmessage = function(event) {
        const trade = JSON.parse(event.data);
        const currentPrice = parseFloat(trade.p).toFixed(5);
        const priceChange = ((currentPrice - initialPrice) / initialPrice) * 100;

        updateTile(symbol, currentPrice, priceChange);
    };
}

function updateTile(symbol, currentPrice, priceChange) {
    const currentPriceElement = document.getElementById(`price-${symbol}`);
    const changeElement = document.getElementById(`change-${symbol}`);
    if (currentPriceElement && changeElement) {
        currentPriceElement.textContent = currentPrice;
        changeElement.textContent = `${priceChange.toFixed(5)}%`;
        changeElement.style.color = priceChange >= 0 ? 'green' : 'red';
    }
}

async function fetchChartData(symbol) {
    const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1d&limit=7`; // Fetches 7 days of daily klines
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data.map(kline => ({ t: kline[0], y: parseFloat(kline[4]) })); // Maps to { t: timestamp, y: closing price }
    } catch (error) {
        console.error("Failed to fetch chart data: ", error);
        return [];
    }
}

let myChart = null; // Global variable to keep track of the current chart

function displayChart(symbol, chartData) {
    // Destroy previous chart if exists
    if (myChart instanceof Chart) {
        myChart.destroy();
    }

    const ctx = document.getElementById('chartCanvas').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: `${symbol} Price (Last 7 Days)`,
                data: chartData,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                x: { // This specifies that the x-axis should be treated as a time scale
                    type: 'time',
                    time: {
                        unit: 'day',
                        tooltipFormat: 'MM/DD/YYYY',
                        displayFormats: {
                            day: 'MM/DD/YYYY'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: { // Configures the y-axis as a linear scale
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Price (USD)'
                    }
                }
            }
        }
    });
}




function showModal() {
    document.getElementById('chartModal').style.display = 'block';
}

function hideModal() {
    document.getElementById('chartModal').style.display = 'none';
}

// Close modal when the 'x' is clicked
document.querySelector('.close').addEventListener('click', hideModal);
