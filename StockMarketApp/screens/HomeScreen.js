import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Alert, TextInput, useColorScheme } from 'react-native';
import {VictoryLine, VictoryChart, VictoryAxis} from 'victory-native';
import Button from '../components/Button1';
import { MarketChart } from '../components/MarketChart';
import { fetchData, fetch_UniqueMarketIndex, fetch_marketPrice } from '../util/api';

export default function HomeScreen({ navigation }) {
  const scheme = useColorScheme(); // detect system color scheme (can be used for future theme references for dark and light themes)
  // state variables
  const [username, setusername] = useState('');
  const [djia, changedjia] = useState({}); // initialize dynamic state variable and function to alter it

  // function for initially calling market index APIs
  async function retrieve_marketindex() {
    const unique_index = await fetch_UniqueMarketIndex();
    const unique_ls = unique_index.map(item => item.index_symbol);
    // console.log('Unique List:', unique_ls);
    let market = {}; // initialize javascript object
    for (let i = 0; i < unique_ls.length; i++) {
      const market_data = await fetch_marketPrice(unique_ls[i]); // call upon function in api.js
      market[unique_ls[i]] = market_data
    };
    changedjia(market); // set dynamic state variable javascript object
  };
   // Call the fetchData function (api.js) when the component mounts (onMount)
  useEffect(() => {
    retrieve_marketindex();
  }, []); // Empty dependency array means this effect runs once on mo
  useEffect(() => {
    console.log('DJIA:', djia);
  }, [djia]); // hook to log 'djia' value whenever its value changes

  // function for handling button press
  function handlePress () {
    setusername('');
  };
  // HTML if function example
  function Intro() {
    if (username !== null || username === '') {
      return <Text style={styles.title}>Hello there {username}!</Text>;
    }
    return <Text style={styles.title}>Hello there!</Text>;
  };
  return (
    <View style={[styles.container, {backgroundColor: 'aliceblue'}]}>
      {/* <Intro/> */}
      {/* <Text style={[styles.title, {color:'black'}]}>Welcome to the Stock Market App</Text> */}
      {/* <Button
        title="Go to Details"
        onPress={() => navigation.navigate('Details')}
      /> */}
  
      {/* <TextInput
        style={[styles.input, {color:'black'}]}
        onChangeText={(name) => setusername(name)}
        value={username} // ensure that the value displayed reflects the reactive variable
        placeholder="Enter Username"
        placeholderTextColor='black'
      /> */}
      {/* // This adds a vertical space of 20 units ('width' also available) */}
      {/* <View style={{height: 20}} ></View>
      <Button
        title="Clear Name"
        onPress={handlePress}
      /> */}
      {/* <Text>{scheme}</Text> */}

      <MarketChart stockData={djia} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  title: {
    fontSize: 20,
    marginBottom: 20
  },
});
