def webpage(webhost):
    #Template HTML
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <title>Turkey Temperature!</title>
    </head>
    <body>

    <div id="time-series-plot"></div>
    
    <div>
    <label for="forecastDuration">Enter forecast duration (minutes): </label>
    <input type="number" id="forecastDuration" value="10" min="1">
    <button onclick="updatePlot()">Forecast</button>
    </div>

    <script>
    function updatePlot() {
        // Fetch JSON with nested data from the server
        fetch('{{webhost}}') // Replace with your server endpoint
        .then(response => response.json())
        .then(jsonData => {
            // Extract top-level fields
            var rate = jsonData.rate;
            var nestedData = jsonData.data;

            // Convert timestamp strings to JavaScript Date objects
            nestedData.forEach(function (entry) {
            entry.timestamp = new Date(entry.timestamp);
            });

            // Extract timestamps and temperatures from nested data
            var timestamps = nestedData.map(function (entry) {
            return entry.timestamp;
            });

            var temperatures = nestedData.map(function (entry) {
            return entry.temperature;
            });

            // User input for forecast duration
            var forecastDurationInput = document.getElementById('forecastDuration');
            var forecastDuration = parseInt(forecastDurationInput.value);

            // Forecast temperature for the specified duration using the "rate"
            var forecastTimestamps = [];
            var forecastTemperatures = [];

            for (var i = 1; i <= forecastDuration; i++) {
            var forecastTimestamp = new Date(timestamps[timestamps.length - 1].getTime() + i * 60 * 1000);
            var forecastTemperature = temperatures[temperatures.length - 1] + rate * i;

            forecastTimestamps.push(forecastTimestamp);
            forecastTemperatures.push(forecastTemperature);
            }

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

            // Create the forecast trace
            var forecastTrace = {
            x: timestamps.concat(forecastTimestamps),
            y: temperatures.concat(forecastTemperatures),
            type: 'scatter',
            mode: 'lines',
            line: {
                color: 'rgb(255, 0, 0)',
            },
            name: 'Forecasted Temperature',
            };

            var layout = {
            title: 'Turkey Temperature!',
            xaxis: {
                title: 'Timestamp',
                tickformat: '%I:%M %p', // Format as HH:MM in 12-hour format
            },
            yaxis: {
                title: 'Temperature',
            },
            };

            var data = [trace, forecastTrace];

            // Use Plotly to create or update the plot
            Plotly.newPlot('time-series-plot', data, layout);
        })
        .catch(error => console.error('Error fetching data:', error));
    }

    // Call the updatePlot function initially
    updatePlot();

    // Set up an interval to update the plot every 5 seconds
    setInterval(updatePlot, 5000);
    </script>

    </body>
    </html>
    """.replace('{{webhost}}', webhost)
    
    return str(html)