const link = 'https://backend-dot-annular-text-410704.de.r.appspot.com';
let post_options = {
    method: 'POST',
    headers: {'Content-Type':'application/json'}
};
// POST request allowing for dynamic SQL queries
export async function fetchData(query) {
    const url = link + '/retrieve' // if connected to kevin_1st
    const payload = {
        'query':query
    };
    const options = {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body:JSON.stringify(payload) // converts query to JSON string to include within request body
    };
    try {
        // console.log('Entering function');
        const response = await fetch(url, options);
        const data = await response.json();
        return data;
    } catch(error) {
        console.log('Something went wrong with the dynamic api call:', error);
    }
};
// function to retrieve all distinct indexes within marketindex table
export async function fetch_UniqueMarketIndex() {
    const url = link + '/retrieve';
    const payload = {'query':"SELECT DISTINCT index_symbol FROM marketindex"};
    post_options.body = JSON.stringify(payload);
    try{
        const response = await fetch(url, post_options);
        const data = await response.json();
        return data;
    } catch (error) {
        console.log('Something went wrong with the fetch_UniqueMarketIndex() API call');
    }
};
// function to retrieve date and close prices from marketindex (specify index symbol)
export async function fetch_marketPrice(index) {
    const url = link + '/retrieve';
    const payload = {'query':"SELECT date, close FROM marketindex WHERE index_symbol = '" + index + "'"};
    post_options.body = JSON.stringify(payload); // [{'date':'XXXX-XX-XX', 'close': XX.X}, {'date': 'XXXX-XX-XX', 'close': XX.X}, ...]
    try{
        const response = await fetch(url, post_options);
        const data = await response.json();
        return data;
    } catch (error) {
        console.log('Something went wrong with the fetch_marketPrice() API call');
    }
};
