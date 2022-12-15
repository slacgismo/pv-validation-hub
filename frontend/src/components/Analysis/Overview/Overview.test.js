import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';
import Overview from "./Overview";

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<Overview/>, {wrapper: BrowserRouter});
        expect(screen.getByRole('heading', {level: 5})).toBeTruthy();
    });
});
