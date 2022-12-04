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
            datasetDetails.file = faker.internet.url() + "/test_pv.zip"});

        const navigate = jest.fn();
        jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);

        // const url = 'http://example.com/test.zip';
        // const link = {
        //     href: url,
        //     download: url.split('/').pop(),
        //     click: jest.fn()
        // };
        // jest.spyOn(document, "createElement").mockImplementation((url) => link);
        // jest.spyOn(link, "click").mockImplementation((url) => link.click);
        render(<Data/>, {
            wrapper: BrowserRouter,
            // wrapperProps: {props: analysis_id}
        });
        await userEvent.click(screen.getByRole('button', {name: /Download Files/i}));
        //screen.debug(datasetDetails);
        // expect(navigate).toHaveBeenCalledWith(datasetDetails.file)

    })
})