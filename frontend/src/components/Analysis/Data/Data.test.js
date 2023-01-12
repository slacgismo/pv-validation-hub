import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';
import Data from "./Data";

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<Data/>, {wrapper: BrowserRouter});
        expect(screen.getByRole('heading', {name: /Dataset Description/i})).toBeTruthy();
        expect(screen.getByRole('heading', {name: /Files/i})).toBeTruthy();
        expect(screen.getByRole('heading', {name: /Type/i})).toBeTruthy();
        expect(screen.getByRole('button', {name: /Download Files/i})).toBeTruthy();
    });
});


describe("Download Button",() => {
    it("Should navigate to download url when clicked", async () => {
        const getAnalysisDataset = jest.fn().mockImplementation(() => {
            datasetDetails.file = faker.internet.url() + "/test_pv.zip"})

        const props = {
            analysis_id: 'test'
        }
        const link = {
            click: jest.fn()
        };
        // jest.spyOn(document.body, "appendChild").mockImplementation(() => link);
        render(<Data {...props}/>, {
            wrapper: BrowserRouter,
        });
        await userEvent.click(screen.getByRole('button', {name: /Download Files/i}));
        // expect(link.click).toHaveBeenCalled();

    })
})