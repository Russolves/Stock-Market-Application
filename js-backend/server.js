const express = require('express');
const app = express();
const mysql = require('mysql2');

app.use(express.json()); // for parsing application/json
const port = process.env.PORT || 3000; // use port available when hosting on gcloud app engine or 3000 when local testing
app.listen(port, () => { // print where server is running (for local production environment)
    console.log(`Server running on port ${port}`);
})
// white list using cors
const cors = require('cors');
app.use(cors({
    origin: function (origin, callback) {
        // Define a whitelist of allowed origins
        const whitelist = [
            'http://localhost:8081' // only allow requests from local environment for now
        ];

        if (!origin || whitelist.indexOf(origin) !== -1) {
            callback(null, true);
        } else {
            callback(new Error('Not allowed by CORS'));
        }
    },
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

require('dotenv').config(); // import the dotenv library
let pool;
try {
    pool = mysql.createPool({ // access through environment variables
        // host:process.env.DB_HOST, // use this for local development
        socketPath: `/cloudsql/${process.env.INSTANCE_CONNECTION_NAME}`, // use this for gcloud app
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        database: process.env.DB_NAME,
        waitForConnections: true,
        connectionLimit: 10, // set connection limit
        queueLimit: 0
    });
} catch (error) {
    console.log('Error for server:', error);
}
// GET request confirmation for server status (default)
app.get('/', (req, res) => {
    res.status(200).send('Backend server GET request successful!');
})
// send GET request to database (stocks table, specify symbol
app.get('/stocks', (req, res) => {
    const symbol = req.headers['symbol']; // Header example: {'Symbol':'2330'}
    // console.log('This is the requested symbol:', symbol);
    try {
        pool.query(`SELECT * FROM stocks WHERE symbol = '${symbol}'`, (err, results, fields) => {
            if (err) {
                res.status(500).send('Something went wrong with the API call for the "stocks" table:', err);
            } else {
                res.status(200).json(results);
            }
        });
    }
    catch (Error) {
        console.log('SQL select error during GET request /stocks:', Error);
    };
});

// send dynamic SQL POST request based on front end requirements (change into separate API endpoints later on)
app.post('/retrieve', (req, res) => {
    const query = req.body['query']; // request body format: {query: 'SELECT * FROM...'}
    console.log('/retrieve API endpoint called!', query);
    try {
        pool.query(query, (err, results, fields) => {
            if (err) {
                res.status(500).send('Something went wrong with the dynamic API call for the "GET" request:', err);
            } else {
                // console.log(`Query successfully executed: ${results}`)
                res.status(200).json(results);
            }
        })
    } catch (Error) {
        console.log('Dynamic GET request error:', Error);
    }
});
