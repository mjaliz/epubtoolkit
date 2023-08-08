import React, {Component} from "react";
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import {ToastContainer} from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Home from "./screens/Home";
import ExtractSentenceScreen from "./screens/ExtractSentenceScreen";

class App extends Component {
    render() {
        return (
            <div className="container vh-100">
                <ToastContainer rtl/>
                <Router>
                    <Routes>
                        <Route exact path="/" element={<Home/>}/>
                        <Route
                            exact
                            path="/extract_sentence"
                            element={<ExtractSentenceScreen/>}
                        />
                    </Routes>
                </Router>
            </div>
        );
    }
}

export default App;
