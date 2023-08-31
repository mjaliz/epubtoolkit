import React from "react";
import { useState } from "react";
import { toast } from "react-toastify";
import http from "../services/httpService";

const SyncAudioScreen = () => {
  const [file, setFile] = useState(null);
  const [bookPath, setBookPath] = useState(undefined);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [bookHasTranslation, setBookHasTranslation] = useState(true);

  const handleSelect = (e) => {
    setFile(e.target.files[0]);
    setSuccess(false);
  };

  const handleCheck = () => {
    setBookHasTranslation(!bookHasTranslation);
  };

  const handleSubmit = async () => {
    if (file !== null) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("has_translation", bookHasTranslation);
      setLoading(true);
      try {
        const { data } = await http.post("/api/sync_audio", formData, {
          headers: { "Content-Type": "multipart/form-data" },
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
    const response = await http.get(
      `/api/download_synced_audio?book_path=${bookPath}`,
      {
        responseType: "blob",
      }
    );
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
      <div class="form-check">
        <input
          class="form-check-input"
          type="checkbox"
          value=""
          id="flexCheckDefault"
          checked={bookHasTranslation}
          onChange={handleCheck}
        />
        <label class="form-check-label" for="flexCheckDefault">
          Book has translation
        </label>
      </div>
      <strong className="mt-2">
        Note: If the book has translation you should first do the translation
        sync first.
      </strong>
      <hr />
      <div className="input-group mb-3">
        <input
          type="file"
          className="form-control"
          id="inputGroupFile02"
          onChange={handleSelect}
        />
      </div>
      <div>
        <button
          className="btn btn-primary"
          type="button"
          disabled={loading || !file || success}
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
          {!loading && <span>Sync Audio</span>}
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

export default SyncAudioScreen;
