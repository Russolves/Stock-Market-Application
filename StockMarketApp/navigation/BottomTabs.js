import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import HomeStackScreen from './HomeStack'; // New Home stack
import DetailsScreen from '../screens/DetailsScreen'; // Assuming you have this screen
// Import other stacks or screens for other tabs
import Ionicons from 'react-native-vector-icons/Ionicons'; // Import Ionicons or any other icon set

const Tab = createBottomTabNavigator();

export default function BottomTabs() {
  return (
      <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Details') {
            iconName = 'information'
          }
          // You can return any component that you like here!
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: 'navy', // Color of the icon when tab is active
        tabBarInactiveTintColor: 'gray', // Color of the icon when tab is inactive
        tabBarStyle: {
            borderTopColor: 'lightgray', // Change the border color here
            backgroundColor: 'white', // Optional: change the background color of the tab bar
        },
      })}
      >
        <Tab.Screen name="Home" component={HomeStackScreen} options={{ headerShown: false }}/>
        <Tab.Screen name="Details" component={DetailsScreen} options={{ headerShown: false }}/>
        {/* Define other screens or stacks for other tabs here */}
      </Tab.Navigator>
  );
}
