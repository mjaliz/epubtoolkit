import React from "react";

const ExtractSentenceScreen = () => {
  const handleSelect = (e) => {
    console.log(e.target.value);
  };
  return (
    <div className="h-100 d-flex align-items-center justify-content-center">
      <form>
        <div id="dropZone" className="drop-zone">
          <div className="form-group">
            <label htmlFor="fileInput">Select file:</label>
            <input
              type="file"
              id="fileInput"
              className="form-control-file"
              onChange={handleSelect}
            />
          </div>
          <span className="text">Drop files here or click to select files</span>
        </div>
      </form>
    </div>
  );
};

export default ExtractSentenceScreen;
