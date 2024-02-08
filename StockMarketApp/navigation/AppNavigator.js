import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import BottomTabs from './BottomTabs';

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <BottomTabs />
    </NavigationContainer>
  );
}
