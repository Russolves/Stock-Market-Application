import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

export default function Button1({ title, onPress }) {
  return (
    <TouchableOpacity onPress={onPress} style={styles.button}>
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: 'navy',
    padding: 15,
    borderRadius: 5,
  },
  text: {
    color: 'mintcream',
    textAlign: 'center',
  },
});
