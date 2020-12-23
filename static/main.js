// Calorie Line Chart
var ctx = document.getElementById('line-chart').getContext('2d');
var chart = new Chart(ctx, {

    // Set type of Chart
    type: 'line',

    // The data for the line chart
    data: {
        labels: time_calories_read_list,
        datasets: [
            {
                label: 'Calories (per reading)', // Interactive rectangular box to enable/disable this dataset
                fill: false, // Shading under the line of this data set
                borderColor: 'rgb(80,200,120)', // Color of the line itself
                data: calorie_consumption_list // Values received from Flask->HTML Context Objects
            }, 
            {
                label: 'Total Calories (per reading)', // Interactive rectangular box to enable/disable this dataset
                fill: false, // Shading under the line of this data set
                borderColor: 'rgb(0, 0, 255)', // Color of the line itself
                data: calorie_accumulation_list// Values received from Flask->HTML Context Objects
            }],
    },

    // Configuration options go here
    options: {}
});


// Macronutrient Distribution (Bar Graph)
var macros_ctx = document.getElementById('macro-chart');
var macros_pie_chart = new Chart(macros_ctx, {

    // Set type of chart
    type: 'pie',
    
    // The data for the pie graph
    data: {
        labels: ['Protein', 'Carbohydrate', 'Fat'], // Interactive labels on the chart
        datasets: [{ 
            label: 'Macronurtient Data',
            data: [curr_protein, curr_carbs, curr_fat], // Values received from Flask->HTML Context Objects
            backgroundColor: ["#3e95cd", "#8e5ea2","#c45850"], // Colors of the respective sections of the pie graph
        }, ]
    },

    // Configuration options go here
    options: {}
});