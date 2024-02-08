import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, TextInput } from 'react-native';
import Button from '../components/Button1';

export default function DetailsScreen({ navigation }) {
  return (
    <View style={[styles.container, {backgroundColor:'white'}]}>
      <Text style={styles.title}>Welcome to the Stock Market App Details Screen</Text>
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
    color:'black' // default color
  },
});
