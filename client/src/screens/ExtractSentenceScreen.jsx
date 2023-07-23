import React from "react";
import {useState} from "react";
import { toast } from "react-toastify";
import http from "../services/httpService";

const ExtractSentenceScreen = () => {
    const [file, setFile] = useState(null)
    const [loading, setLoading] = useState(false)
    const handleSelect = (e) => {
        setFile(e.target.files[0])
    };
    const handleSubmit = async () => {
        if (file !== null) {
            const formData = new FormData()
            formData.append('file', file)
            setLoading(true)
            try {
                const {data} = await http.post("/extract_sentence", formData, {headers: {"Content-Type": "multipart/form-data"}})
                console.log(data)
            } catch (e) {
                console.log(e)
                toast.error(e.response.statusText)
            }
            setLoading(false)
        }
    }
    return (
        <div className="h-100 d-flex flex-column align-items-start justify-content-start py-5">
            <div className="input-group mb-3">
                <input type="file" className="form-control" id="inputGroupFile02" onChange={handleSelect}/>
            </div>
            <button className="btn btn-primary" type="button" disabled={loading || !file} onClick={handleSubmit}>
                {loading && (
                    <>
                        <span className="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
                        <span className="m-2">Processing...</span>
                    </>
                )}
                Extract Sentence
            </button>
        </div>
    );
};

export default ExtractSentenceScreen;
