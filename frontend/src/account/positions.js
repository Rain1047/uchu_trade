// balance.js
import React, { useState, useEffect } from 'react';

function Positions() {
    const [positions, setPositions] = useState(null);
    const [totalEq, setTotalEq] = useState(null);
    const [isoEq, setIsoEq] = useState(null);
    const [details, setDetails] = useState([]);
    const [sumValue, setSumValue] = useState(null);

    const fetchData = () => {
        fetch("http://127.0.0.1:8000/get_positions")
            .then(response => response.json())
            .then(data => {
                setPositions(data);
                if (data && data.data && data.data.length > 0) {
                    // const totalEqValue = parseFloat(data.data[0].totalEq).toFixed(4);
                    // setTotalEq(totalEqValue);
                    // const isoEqValue = parseFloat(data.data[0].isoEq).toFixed(4);
                    // setIsoEq(isoEqValue);
                    // // Calculate the sum of totalEq and isoEq
                    // const sumValue = (parseFloat(totalEqValue) + parseFloat(isoEqValue)).toFixed(4);
                    // setSumValue(sumValue);
                    // const detailedBalances = data.data[0].details.map(detail => ({
                    //     ...detail,
                    //     eq: parseFloat(detail.eq).toFixed(2),
                    //     disEq: parseFloat(detail.disEq).toFixed(2)
                    // }));
                    // setDetails(detailedBalances);
                }
            })
            .catch(error => {
                console.error('Error fetching balance:', error);
                setPositions({ error: true });
            });
    };

    useEffect(() => {
        // Fetch data initially
        fetchData();

        // Set up interval to fetch data every 5 seconds
        const intervalId = setInterval(fetchData, 5000);

        // Clean up interval on component unmount
        return () => clearInterval(intervalId);
    }, []);


    return (
        <div>
            <h4>Position Data</h4>
            {positions && <pre>{JSON.stringify(positions, null, 2)}</pre>}
            <h5>美金层面权益+仓位权益</h5>
            <p>{sumValue}</p>
            <h5>美金层面权益</h5>
            <p>{totalEq}</p>
            <h5>仓位权益</h5>
            <p>{isoEq}</p>
            <h5>Details</h5>
            <ul>
                {details.map((item, index) => (
                    <li key={index}>
                        Currency: {item.ccy}, disEq: {item.disEq}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Positions;