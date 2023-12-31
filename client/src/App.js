import React, {Component} from "react";
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import {ToastContainer} from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import HomeScreen from "./screens/HomeScreen";
import ExtractSentenceScreen from "./screens/ExtractSentenceScreen";
import SyncAudioScreen from "./screens/SyncAudioScreen";
import SyncTranslationScreen from "./screens/SyncTranslationScreen";

class App extends Component {
    render() {
        return (
            <div className="container vh-100">
                <ToastContainer rtl/>
                <Router>
                    <Routes>
                        <Route exact path="/" element={<HomeScreen/>}/>
                        <Route
                            exact
                            path="/extract_sentence"
                            element={<ExtractSentenceScreen/>}
                        />
                        <Route
                            exact
                            path="/sync_audio"
                            element={<SyncAudioScreen/>}
                        />
                        <Route
                            exact
                            path="/sync_translation"
                            element={<SyncTranslationScreen/>}
                        />
                    </Routes>
                </Router>
            </div>
        );
    }
}

export default App;
