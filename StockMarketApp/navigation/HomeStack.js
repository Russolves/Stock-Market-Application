import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from '../screens/HomeScreen';

const HomeStack = createStackNavigator();

function HomeStackScreen() {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="HomeScreen" component={HomeScreen} options={{ headerShown: false }} />
      {/* <HomeStack.Screen name="Details" component={DetailsScreen} /> */}
      {/* Add more screens as needed */}
    </HomeStack.Navigator>
  );
}

export default HomeStackScreen;
