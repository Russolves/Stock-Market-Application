const link = 'https://backend-dot-annular-text-410704.de.r.appspot.com';
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