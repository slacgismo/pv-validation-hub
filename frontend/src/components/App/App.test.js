import React from "react";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import App from "./App";

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<App />);
    });
});