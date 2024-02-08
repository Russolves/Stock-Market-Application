import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Alert, TextInput, useColorScheme } from 'react-native';
import Button from '../components/Button1';
import { fetchData } from '../util/api';

export default function HomeScreen({ navigation }) {
  const scheme = useColorScheme(); // detect system color scheme
  // state
  const [username, setusername] = useState('');
  const [djia, changedjia] = useState([]);
  // function for calling API
  async function retrieve_marketindex() {
    console.log('Entering retrieve market index');
    let query = "SELECT DISTINCT index_symbol FROM marketindex";
    const unique_index = await fetchData(query);
    const unique_ls = unique_index.map(item => item.index_symbol);
    // console.log('Unique List:', unique_ls);
    for (let i = 0; i < unique_ls.length; i++) {
      query = `SELECT date, close FROM marketindex WHERE index_symbol = '${unique_ls[i]}'`
      const market_data = await fetchData(query);
    };

  };
   // Call fetchData when the component mounts
  useEffect(() => {
    retrieve_marketindex();
  }, []); // Empty dependency array means this effect runs once on mount

  // function for handling button press
  function handlePress () {
    setusername('');
  };
  // if function example
  function Intro() {
    if (username !== null || username === '') {
      return <Text style={styles.title}>Hello there {username}!</Text>;
    }
    return <Text style={styles.title}>Hello there!</Text>;
  };
  return (
    <View style={[styles.container, {backgroundColor: 'aliceblue'}]}>
      <Intro/>
      <Text style={[styles.title, {color:'black'}]}>Welcome to the Stock Market App</Text>
      {/* <Button
        title="Go to Details"
        onPress={() => navigation.navigate('Details')}
      /> */}
  
      <TextInput
        style={[styles.input, {color:'black'}]}
        onChangeText={(name) => setusername(name)}
        value={username} // ensure that the value displayed reflects the reactive variable
        placeholder="Enter Username"
        placeholderTextColor='black'
      />
      {/* // This adds a vertical space of 20 units ('width' also available) */}
      <View style={{height: 20}} ></View>
      <Button
        title="Clear Name"
        onPress={handlePress}
      />
      {username && <Text>{username}</Text>}
      {/* <Text>{scheme}</Text> */}
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
