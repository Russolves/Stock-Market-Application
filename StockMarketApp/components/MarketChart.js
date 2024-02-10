import React, { useState, useEffect } from 'react';
import { Platform, Text, View, StyleSheet } from 'react-native';
import { VictoryLine, VictoryChart, VictoryAxis, VictoryTheme, VictoryBar, VictoryZoomContainer } from 'victory-native';
import moment from 'moment-timezone';
import { parse } from 'react-native-svg';

export const MarketChart = ({ stockData }) => { // Accept `stockData` as a prop
    // // Conditional rendering: Render chart only if `stockData` is not empty
    // if (stockData.length === 0) {
    // return <Text>Loading chart data...</Text>;
    // }
    const [parsedStockData, setparsedStockData] = useState([]);
    const props = Platform.select({
        web: {},
        default: {
            accessibilityHint: "Description of the action",
        },
    });
    function Graph() {
        const marketNames = Object.keys(stockData);
        // Check if stockData is empty
        if (marketNames.length === 0) {
            return <Text>Loading chart data...</Text>;
        }
        // Map each market to a VictoryChart component
        const charts = marketNames.map(marketName => {
            let data = stockData[marketName].map(item => ({
                ...item,
                date: moment(item.date).format('YYYY/M/D') // Format date
            }));
            return (
                <View key={marketName} style={[styles.barchart]}>
                    <Text>{marketName}</Text>
                    <VictoryChart
                        scale={{ x: "time" }}
                        containerComponent={<VictoryZoomContainer />}
                    >
                        <VictoryAxis
                            tickFormat={(tick) => tick}
                            tickCount={10}
                        />
                        <VictoryAxis dependentAxis />
                        <VictoryLine
                            data={data}
                            x="date"
                            y="close"
                            style={{
                                data: { stroke: "red", strokeWidth: 2 }, // Customize line color and thickness
                            }}
                        />
                    </VictoryChart>
                </View>
            );
        });
        // Return a fragment containing all charts
        return <>{charts}</>;
    }    
    // useEffect(() => {
    //     return parsedStockData;
    //   }, [parsedStockData]);

    return (    
    <View>
        <Graph />
    </View>
    );
};

const styles = StyleSheet.create({
    barchart:{
        flex: 0.1,
        alignSelf:'flex-start',
        padding:'10px',
        height: '30%',
        width:'30%'
    }
});
