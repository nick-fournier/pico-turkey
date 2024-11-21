// Check if local storage contains data, if not, initialize with empty arrays
var stringTimestamps = JSON.parse(localStorage.getItem('timestamps')) || [];
var temperatures = JSON.parse(localStorage.getItem('temperatures')) || [];

// Function to clear local storage
function clearLocalStorage() {
  console.log('Clearing local storage');
  localStorage.clear();
  // Clear current arrays as well
  stringTimestamps = [];
  timestamps = [];
  temperatures = [];
  // Update the plot after clearing local storage
  updatePlot();
}

// Function to format the time to completion as HH:MM:SS
function formatTimeToCompletion(TTC) {
  var hours = Math.floor(TTC / 60);
  var minutes = Math.floor(TTC % 60);
  var seconds = Math.floor((TTC * 60) % 60);
  return padZero(hours) + ':' + padZero(minutes) + ':' + padZero(seconds);
}

// Function to pad zero to single-digit numbers
function padZero(num) {
  return num < 10 ? '0' + num : num;
}

function updatePlot() {

  // Get the latest time stamp, if any.
  var lastTimestampString = stringTimestamps[stringTimestamps.length - 1];

  // If there is no timestamp, set the current timestamp to 0 to fetch all data
  if (lastTimestampString === undefined) {
    lastTimestampString = 0;
  }

  // Fetch current data from /data/current endpoint which is a JSON with timestamp, temperature, rate, and stdev
  // Fetch streaming data from /data/stream/<from_timestamp> endpoint with the format [[timestamp, temperature], ...]
  const current_request = fetch('/data/current').then(response => response.json());
  const stream_request = fetch('/data/stream/' + lastTimestampString).then(response => response.text());

  // Process the fetched data
  Promise.all([current_request, stream_request])
    .then(([currentJSON, dataString]) => {
      // Extract the current data from the fetched data and convert to float
      var currentTemperature = parseFloat(currentJSON.temperature);
      var rate = parseFloat(currentJSON.rate);

      // Define regular expression patterns for extracting timestamps and temperatures
      const timestampPattern = /\[([\d\s:-]+),\s([\d.]+)\]/g;

      // Extract matches using the regular expression and append to the arrays
      // If the timestamp is already in the array, skip it
      let match;
      while ((match = timestampPattern.exec(dataString)) !== null) {
        if (stringTimestamps.includes(match[1])) {
          continue;
        } else {
          stringTimestamps.push(match[1]);
          temperatures.push(parseFloat(match[2]));
        }
      }

      // Store data in local storage as original string
      localStorage.setItem('timestamps', JSON.stringify(stringTimestamps.map(String)));
      localStorage.setItem('temperatures', JSON.stringify(temperatures));

      // Convert timestamps from string to Date objects
      timestamps = stringTimestamps.map(timestamp => new Date(timestamp));

      // User input for forecast duration
      var forecastDurationInput = document.getElementById('forecastDuration');
      var forecastDuration = parseInt(forecastDurationInput.value);

      // User input for target temperature
      var targetTemperatureInput = document.getElementById('targetTemperature');
      var targetTemperature = parseFloat(targetTemperatureInput.value);
      
      // Create the time series mountain plot
      var trace = {
        x: timestamps,
        y: temperatures,
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        line: {
          color: 'rgb(0, 100, 255)',
        },
        name: 'Actual Temperature',
      };

      // Calculate forecasted timestamps and temperatures
      var forecastTimestamps = [];
      var forecastTemperatures = [];

      for (var i = 0; i <= forecastDuration; i++) {
        var forecastTimestamp = new Date(timestamps[timestamps.length - 1].getTime() + i * 60 * 1000);
        var forecastTemperature = temperatures[temperatures.length - 1] + rate * i;

        forecastTimestamps.push(forecastTimestamp);
        forecastTemperatures.push(forecastTemperature);
      }

      // Create the forecast trace with a dotted line
      var forecastTrace = {
        x: forecastTimestamps,
        y: forecastTemperatures,
        type: 'scatter',
        mode: 'lines',
        line: {
          color: 'rgb(255, 0, 0)',
          dash: 'dot',  // Set the line style to dotted
        },
        name: 'Forecasted Temperature',
      };

      var layout = {
        xaxis: {
          title: {
            // text: 'Timestamp',
            font: {
              color: 'white',  // X-axis title text color
            },
          },
          tickfont: {
            color: 'white',  // Tick label text color
          },
          tickformat: '%I:%M %p', // Format as HH:MM in 12-hour format
          showgrid: true,  // Display grid lines on the x-axis
          gridcolor: 'gray',  // Set grid lines color
        },
        yaxis: {
          title: {
            text: 'Temperature (F)',
            font: {
              color: 'white',  // Y-axis title text color
            },
          },
          tickfont: {
            color: 'white',  // Y-axis tick label text color
          },
          showgrid: true,  // Display grid lines on the y-axis
          gridcolor: 'gray',  // Set grid lines color
        },
        legend: {
          font: {
            color: 'white',  // Legend font color
          },
          x: 0,   // Set x to 0 for left alignment
          y: 1.2, // Set y to -0.2 for below the chart
        },
        paper_bgcolor: 'rgba(0,0,0,0.1)',  // Transparent background color of the chart
        plot_bgcolor: 'rgba(0,0,0,0)',     // Transparent background color of the plot area
      };

      // Calculate estimated time to completion
      var TTC = (targetTemperature - currentTemperature) / rate;
      var data = [trace, forecastTrace];

      // Use Plotly to create or update the plot
      Plotly.newPlot('time-series-plot', data, layout);

      // Display the current temperature with plus-minus symbol
      var currentTemperatureDiv = document.getElementById('currentTemperature');
      currentTemperatureDiv.innerHTML = '' + currentTemperature.toFixed(2) + ' °F ± ' + rate.toFixed(2) + ' °F/min';

      // Display the estimated time to completion
      var completionCalculationDiv = document.getElementById('completionCalculation');
      if (!isNaN(TTC) && isFinite(TTC) && TTC > 0) {
        var completionTimeString = formatTimeToCompletion(TTC);
      } else {
        var completionTimeString = 'N/A';
      }        
      completionCalculationDiv.innerHTML = 'Estimated Time: ' + completionTimeString;
    })
    .catch(error => console.error('Error fetching data:', error));
}

// Call the updatePlot function initially
updatePlot();

// Set up an interval to update the plot every 5 seconds
setInterval(updatePlot, 5000);