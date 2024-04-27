import React, { useState, useEffect } from 'react';
import { Platform, Text, View, StyleSheet, ScrollView } from 'react-native';
import { VictoryLine, VictoryChart, VictoryAxis, VictoryTheme, VictoryBar, VictoryZoomContainer } from 'victory-native';
import names from './Names';
import moment from 'moment-timezone';
import { parse } from 'react-native-svg';

export const MarketChart = ({ stockData }) => { // Accept `stockData` as a prop
    
    // // Conditional rendering: Render chart only if `stockData` is not empty
    // if (stockData.length === 0) {
    // return <Text>Loading chart data...</Text>;
    // }

    // state variables used for display [variable, function_to_set_variable]
    const [parsedStockData, setparsedStockData] = useState([]);
    const props = Platform.select({
        web: {},
        default: {
            accessibilityHint: "Description of the action",
        },
    });
    const market_order = [
        '^TWII',
        '^DJI',
        '^GSPC',
        '^IXIC',
        '^HSI',
        '^N225'
    ];
    // function for filtering for recent (365 days) of data
    function filterRecentData(data) {
        // const endDate = moment(); // today
        // const startDate = endDate.clone().subtract(days, 'days');
        // return data.filter(item => {
        //     const itemDate = moment(item.Date);
        //     return itemDate.isBetween(startDate, endDate, null, '[]'); // inclusive
        // })
        return data.slice(-365);
    };
    function Graph() {
        let marketNames = Object.keys(stockData);
        // Check if stockData is empty
        if (marketNames.length === 0) {
            return <Text>Loading chart data...</Text>;
        }
        
        marketNames = marketNames.filter(item =>!item in market_order);
        marketNames = market_order.concat(marketNames); // order the list
        // Map each market to a VictoryChart component
        const charts = marketNames.map(marketName => {
            let data = filterRecentData(stockData[marketName]).map(item => ({
                ...item,
                date: moment(item.date).format('YYYY/M/D') // Format date
            }));
            const most_recent = data.slice(-1)[0]; // get most recent closing price
            const recent_price = most_recent['close']
            const average = data.map(obj => parseFloat(obj['close'])) // array of close prices
            const sum = average.reduce((accumulator, currentValue) => accumulator + currentValue);
            const average_value = sum/data.length; 
            let market_average = []; // initialize empty array for average
            // create javascript object for average
            for (let i = 0; i < data.length; i++) {
                let obj = {};
                obj["date"] = data[i]['date'];
                obj["average"] = average_value;
                market_average.push(obj);
            };
            // calculate percentage decrease from past year average
            const percentage_difference = (((recent_price - average_value)/average_value)*100).toFixed(2);
            function Negative() {
                let display = '';
                if (percentage_difference >= 0) {
                    display = '+' + percentage_difference.toString() + '%';
                    return <Text>{display}</Text>
                }
                display = percentage_difference.toString() + '%';
                return <Text>{display}</Text>
            };
            const display_name = names["Market"][marketName]["chinese"]; // using chinese full name for now
            return (
                <View key={marketName} style={styles.barchart}>
                    {/* <Text>{marketName}</Text> */}
                    <View style={{height: '0.1%'}} ></View>
                    <View style={styles.chartRow}>
                        <View style={styles.textColumn}>
                            <Text>{display_name}</Text>
                            <Text>{recent_price}</Text>
                            <Negative />
                            {/* <Text>{percentage_difference}</Text> */}
                        </View>
                        <View style={styles.chartColumn}>
                            <VictoryChart
                                // style={styles.chart}
                                scale={{ x: "time" }}
                                containerComponent={<VictoryZoomContainer />}
                            >
                                <VictoryAxis
                                    tickFormat={(tick) => tick}
                                    tickCount={10}
                                    style={{
                                        axis: {stroke: "grey"},
                                        ticks: {stroke: "transparent"},
                                        tickLabels: {fill: "transparent"}
                                }}
                                />
                                <VictoryAxis dependentAxis style={{
                                    axis: { stroke: "grey"},
                                    ticks: { stroke: "transparent"},
                                    tickLabels: {fill: "transparent"}
                                }} />
                                <VictoryLine 
                                    data={market_average}
                                    x="date"
                                    y="average"
                                    style={{
                                        data: {
                                            stroke: "grey",
                                            strokeWidth: 2,
                                            strokeDasharray: [4, 5],
                                        }
                                    }}
                                />
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
                    </View>
                    {/* <View style={{height:100}}></View> */}
                </View>
            );
        });
        // Return a fragment containing all charts
        return (<ScrollView style={styles.scrollView}>{charts}</ScrollView>);
    }
    // // this is run when the page is first rendered (onMount)
    // useEffect(() => {
    //     return parsedStockData;
    //   }, [parsedStockData]);

    return (    
        <Graph />
    );
};

const styles = StyleSheet.create({
    chartRow: {
        flexDirection: 'row',
        justifyContent: 'flex-start',
        alignItems: 'center',
        // marginBottom: 20, // Add some bottom margin to each row
    },
    textColumn: {
        width: '20%',
        padding:5,
    },
    chartColumn: {
        flex: 1,
    },
    scrollView:{
        alignSelf:'center',
        // flexDirection: 'row',
        flexGrow: 1,
        // paddingVertical: 20,
        // height:'5%',
        width:'50%',
        height:'25%',
    },
    barchart:{
        // flex: 0.1,
        justifyContent:'center',
        alignItems:'center',
        // height: 300,
        // width:'30%',
        // padding:5,
        // marginVertical:20,
        borderRadius: 10,
        overflow:'hidden',
        marginVertical: 10,
    },
});
