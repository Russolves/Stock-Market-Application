const express = require('express');
const app = express();
const port = 3000;
const mysql = require('mysql2');

app.use(express.json()); // for parsing application/json
app.listen(port, () => { // print where server is running (for local production environment)
    console.log(`Server running on port ${port}`);
})
require('dotenv').config(); // import the dotenv library

const pool = mysql.createPool({ // access through environment variables
    host:process.env.DB_HOST,
    user:process.env.DB_USER,
    password:process.env.DB_PASSWORD,
    database:process.env.DB_NAME,
    waitForConnections: true,
    connectionLimit: 10, // set connection limit
    queueLimit: 0
});

// send GET request to database (stocks table)
app.get('/stocks', (req, res) => {
    pool.query("SELECT * FROM stocks WHERE symbol = '2330'", (err, results, fields) => {
        if (err) {
            res.status(500).send('Something went wrong with the API call for the "stocks" table:', err);
        } else {
            // console.log('These are the results:', results); // results is a list!
            res.status(200).json(results);
        }
    });
});