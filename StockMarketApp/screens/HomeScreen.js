import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, TextInput } from 'react-native';
import Button from '../components/Button';

export default function HomeScreen({ navigation }) {
  // state
  const [username, setusername] = useState(null);
  // function for handling button press
  function handlePress () {
    setusername(null);
  };
  // if function example
  function Intro() {
    if (username !== null || username === '') {
      return <Text style={styles.title}>Hello there {username}!</Text>;
    }
    return <Text style={styles.title}>Hello there!</Text>;
  };

  return (
    <View style={styles.container}>
      <Intro/>
      <Text style={styles.title}>Welcome to the Stock Market App</Text>
      <Button
        title="Go to Details"
        onPress={() => navigation.navigate('Details')}
      />
  
      <TextInput
        style={styles.input}
        onChangeText={(name) => setusername(name)}
        placeholder="Enter Username"
      />
      <Button
        title="Clear Name"
        onPress={handlePress}
      />
      {username && <Text>{username}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 20,
    marginBottom: 20,
  },
});
