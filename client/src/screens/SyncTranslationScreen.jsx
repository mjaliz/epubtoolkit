import React from "react";
import {useState} from "react";
import {toast} from "react-toastify";
import http from "../services/httpService";

const SyncTranslationScreen = () => {
    const [bookFile, setBookFile] = useState(null);
    const [translationFile, setTranslationFile] = useState(null);
    const [bookPath, setBookPath] = useState(undefined);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const handleSelectBook = (e) => {
        setBookFile(e.target.files[0]);
        setSuccess(false)
    };
    const handleSelectTranslation = (e) => {
        setTranslationFile(e.target.files[0]);
        setSuccess(false)
    };
    const handleSubmit = async () => {
        if (bookFile !== null && translationFile !== null) {
            const formData = new FormData();
            formData.append("book_file", bookFile);
            formData.append("translation_file", translationFile);
            setLoading(true);
            try {
                const {data} = await http.post("/sync_translation", formData, {
                    headers: {"Content-Type": "multipart/form-data"},
                });
                setSuccess(true);
                setBookPath(data.data);
            } catch (e) {
                toast.error(e.response.data?.message.text);
            }
            setLoading(false);
        }
    };
    const handleDownload = async () => {
        const response = await http.get(`/download_synced_translation?book_path=${bookPath}`, {
            responseType: "blob",
        });
        let headerLine = response.headers["content-disposition"];
        let startFileNameIndex = headerLine.indexOf('"') + 1;
        let endFileNameIndex = headerLine.lastIndexOf('"');
        let filename = headerLine.substring(startFileNameIndex, endFileNameIndex);
        const url = window.URL.createObjectURL(response.data);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
    };
    return (
        <div className="h-100 d-flex flex-column align-items-start justify-content-start py-5">
            <div className="input-group mb-3">
                <label className="input-group-text" htmlFor="book">Book</label>
                <input
                    type="file"
                    className="form-control"
                    id="book"
                    onChange={handleSelectBook}
                />
            </div>
            <div className="input-group mb-3">
                <label className="input-group-text" htmlFor="translation">Translation</label>
                <input
                    type="file"
                    className="form-control"
                    id="translation"
                    onChange={handleSelectTranslation}
                />
            </div>
            <div>
                <button
                    className="btn btn-primary"
                    type="button"
                    disabled={loading || !bookFile || !translationFile || success}
                    onClick={handleSubmit}
                >
                    {loading && (
                        <>
              <span
                  className="spinner-grow spinner-grow-sm"
                  role="status"
                  aria-hidden="true"
              ></span>
                            <span className="m-2">Processing...</span>
                        </>
                    )}
                    {!loading && <span>Sync Translation</span>}
                </button>
                {success && bookPath && (
                    <button className="btn btn-success m-2" onClick={handleDownload}>
                        Save
                    </button>
                )}
            </div>
        </div>
    );
};

export default SyncTranslationScreen;
