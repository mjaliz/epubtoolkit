import React from "react";
import "./extractSentence.css";

const ExtractSentenceScreen = () => {
  return (
    <div className="h-100 d-flex align-items-center justify-content-center">
      <form>
        <div id="dropZone" className="drop-zone">
          <div className="form-group">
            <label for="fileInput">Select file:</label>
            <input type="file" id="fileInput" className="form-control-file" />
          </div>
          <span className="text">Drop files here or click to select files</span>
        </div>
      </form>
    </div>
  );
};

export default ExtractSentenceScreen;
