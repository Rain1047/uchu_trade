import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import Button from '@material-ui/core/Button';

const useStyles = makeStyles((theme) => ({
    form: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginTop: theme.spacing(2),
    },
    input: {
        marginBottom: theme.spacing(2),
    },
    button: {
        marginTop: theme.spacing(2),
    },
}));


function Order() {

    const classes = useStyles();

    // 使用state来跟踪表单输入
    const [orderDetails, setOrderDetails] = useState({
        instId: '',
        tdMode: 'cash',
        sz: '',
        side: 'buy',
        ordType: 'limit',
        px: '',
        // Add other fields here with initial values if needed
    });


    // 新状态用于存储下单操作的响应
    const [orderResponse, setOrderResponse] = useState(null);
    const [isOrderPlaced, setIsOrderPlaced] = useState(false);

    // 处理输入变化事件
    // 处理输入变化事件
    const handleChange = (e) => {
        const { name, value } = e.target;
        console.log(`Changed ${name} to: ${value}`);
        setOrderDetails((prevState) => ({
            ...prevState,
            [name]: value,
        }));
    };
    // 发送订单到后端
    const placeOrder = () => {
        fetch('http://127.0.0.1:8000/place_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderDetails),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                // 存储响应和更新状态以表明订单已下达
                setOrderResponse(data);
                setIsOrderPlaced(true);
            })
            .catch((error) => {
                console.error('Error placing order:', error);
            });
    };

    // 处理表单提交事件
    const handleSubmit = (e) => {
        e.preventDefault();
        placeOrder();
    };

    return (
        <div>
            <form className={classes.root} noValidate autoComplete="off">
                <TextField id="standard-basic" label="Standard"/>
                <TextField id="filled-basic" label="Filled" variant="filled"/>
                <TextField id="outlined-basic" label="Outlined" variant="outlined"/>
            </form>

            {/*<form onSubmit={handleSubmit}>*/}
            {/*    <label htmlFor="instId">产品ID：</label>*/}
            {/*    <input*/}
            {/*        type="text"*/}
            {/*        name="instId"*/}
            {/*        value={orderDetails.instId}*/}
            {/*        onChange={handleChange}*/}
            {/*        placeholder="instId Name"*/}
            {/*        required*/}
            {/*    />*/}
            {/*    <br/> /!* Add a line break here *!/*/}
            {/*    <label htmlFor="side">交易模式：</label>*/}
            {/*    <select*/}
            {/*        name="tdMode"*/}
            {/*        value={orderDetails.tdMode}*/}
            {/*        onChange={handleChange}*/}
            {/*        required*/}
            {/*    >*/}
            {/*        <option value="cash">现金</option>*/}
            {/*        <option value="isolated">逐仓</option>*/}
            {/*        <option value="cross">全仓</option>*/}

            {/*    </select>*/}
            {/*    <br/>*/}
            {/*    <label htmlFor="sz">购买数量：</label>*/}
            {/*    <input*/}
            {/*        type="number"*/}
            {/*        name="sz"*/}
            {/*        value={orderDetails.sz}*/}
            {/*        onChange={handleChange}*/}
            {/*        min="1"*/}
            {/*        required*/}
            {/*    />*/}
            {/*    <br/> /!* Add a line break here *!/*/}
            {/*    /!* Add a select dropdown for order direction *!/*/}
            {/*    <label htmlFor="side">订单方向：</label>*/}
            {/*    <select*/}
            {/*        name="side"*/}
            {/*        value={orderDetails.side}*/}
            {/*        onChange={handleChange}*/}
            {/*        required*/}
            {/*    >*/}
            {/*        <option value="buy">买入</option>*/}
            {/*        <option value="sell">卖出</option>*/}
            {/*    </select>*/}
            {/*    <br/> /!* Add a line break here *!/*/}
            {/*    <label htmlFor="ordType">订单类型：</label>*/}
            {/*    <select*/}
            {/*        name="ordType"*/}
            {/*        value={orderDetails.ordType}*/}
            {/*        onChange={handleChange}*/}
            {/*        required*/}
            {/*    >*/}
            {/*        /!* ... Other options ... *!/*/}
            {/*        <option value="limit">限价单</option>*/}
            {/*        <option value="market">市价单</option>*/}
            {/*    </select>*/}
            {/*    <br/> /!* Add a line break here *!/*/}

            {/*    /!* Conditionally render px input field based on ordType *!/*/}
            {/*    {orderDetails.ordType === 'limit' && (*/}
            {/*        <div>*/}
            {/*            <label htmlFor="px">委托价格：</label>*/}
            {/*            <input*/}
            {/*                type="number"*/}
            {/*                name="px"*/}
            {/*                value={orderDetails.px}*/}
            {/*                onChange={handleChange}*/}
            {/*                min="0" // Set min value as per your requirement*/}
            {/*                required*/}
            {/*            />*/}
            {/*            <br/> /!* Add a line break here *!/*/}
            {/*        </div>*/}
            {/*    )}*/}
            {/*    <br/> /!* Add a line break here *!/*/}
            {/*    <button type="submit">Place Order</button>*/}
            {/*</form>*/}

            <form className={classes.form} onSubmit={handleSubmit}>
                <TextField
                    className={classes.input}
                    id="instId"
                    label="产品ID"
                    variant="outlined"
                    name="instId"
                    value={orderDetails.instId}
                    onChange={handleChange}
                    placeholder="instId Name"
                    required
                />
                <TextField
                    className={classes.input}
                    id="sz"
                    label="购买数量"
                    variant="outlined"
                    type="number"
                    name="sz"
                    value={orderDetails.sz}
                    onChange={handleChange}
                    inputProps={{min: 1}}
                    required
                />
                {orderDetails.ordType === 'limit' && (
                    <TextField
                        className={classes.input}
                        id="px"
                        label="委托价格"
                        variant="outlined"
                        type="number"
                        name="px"
                        value={orderDetails.px}
                        onChange={handleChange}
                        inputProps={{min: 0}}
                        required
                    />
                )}
                <Select
                    className={classes.input}
                    label="交易模式"
                    variant="outlined"
                    name="tdMode"
                    value={orderDetails.tdMode}
                    onChange={handleChange}
                    required
                >
                    <MenuItem value="cash">现金</MenuItem>
                    <MenuItem value="isolated">逐仓</MenuItem>
                    <MenuItem value="cross">全仓</MenuItem>
                </Select>
                <Select
                    className={classes.input}
                    label="订单方向"
                    variant="outlined"
                    name="side"
                    value={orderDetails.side}
                    onChange={handleChange}
                    required
                >
                    <MenuItem value="buy">买入</MenuItem>
                    <MenuItem value="sell">卖出</MenuItem>
                </Select>
                <Select
                    className={classes.input}
                    label="订单类型"
                    variant="outlined"
                    name="ordType"
                    value={orderDetails.ordType}
                    onChange={handleChange}
                    required
                >
                    <MenuItem value="limit">限价单</MenuItem>
                    <MenuItem value="market">市价单</MenuItem>
                </Select>

                <Button className={classes.button} type="submit" variant="contained" color="primary">
                    Place Order
                </Button>
            </form>

            {isOrderPlaced && orderResponse && (
                <div>
                    <h3>Order Confirmation</h3>
                    <p>Status: {orderResponse.status}</p>
                    <p>Order ID: {orderResponse.order_id}</p>
                    {/* Add additional information based on your response structure */}
                    {orderResponse.data && (
                        <div>
                            <p>clOrdId: {orderResponse.data[0].clOrdId}</p>
                            <p>ordId: {orderResponse.data[0].ordId}</p>
                            {/* Add more fields as needed */}
                        </div>
                    )}
                    <p>In Time: {orderResponse.inTime}</p>
                    <p>Out Time: {orderResponse.outTime}</p>
                </div>
            )}

            {!isOrderPlaced && orderResponse && (
                <div>
                    <h3>Error</h3>
                    <p>Status: {orderResponse.code}</p>
                    <p>Message: {orderResponse.msg}</p>
                </div>
            )}

        </div>
    );
}

export default Order;
