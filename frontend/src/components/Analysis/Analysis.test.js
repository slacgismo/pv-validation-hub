import React from "react";
import { render, screen, cleanup, getAllByRole } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';
import Analysis from "./Analysis";
import { selectUnstyledClasses } from "@mui/base";

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<div id="root"><Analysis/></div>, {wrapper: BrowserRouter});
        expect(screen.getByRole('heading', {level: 2})).toBeTruthy();
    });
});

describe("Selecting Tabs", () => {
    it("Should show Upload Algorithm button when Leaderboard tub was chosen", async () => {
        render(<div id="root"><Analysis/></div>, {wrapper: BrowserRouter});
        const tabLearderboard = screen.getByRole('tab', {name: 'Leaderboard'});
        expect(tabLearderboard).toBeTruthy();
        await userEvent.click(tabLearderboard);
        expect(tabLearderboard).toHaveAttribute("aria-selected","true");
        expect(screen.getByRole('button', {name: 'Upload Algorithm'})).toBeTruthy();
    });

});

describe("Uploading Algorithm", () => {
    it("Should show the Upload Algorithm screen when the button was pressed", async () => {
        render(<div id="root"><Analysis/></div>, {wrapper: BrowserRouter});
        // Select the Leaderboard tub
        const tabLearderboard = screen.getByRole('tab', {name: 'Leaderboard'});
        await userEvent.click(tabLearderboard);
        // Open the Upload Algorithm page when the Upload Algorithm button is pressed
        const submissionButton = screen.getByRole('button', {name: 'Upload Algorithm'});
        await userEvent.click(submissionButton);
        expect(screen.getByText("PV Validation Hub Algorithm Upload")).toBeTruthy();
    });

    it("Should close the Upload Algorithm screen when the cancel icon was pressed", async () => {
        render(<div id="root"><Analysis/></div>, {wrapper: BrowserRouter})
        // Select the Leaderboard tub
        const tabLearderboard = screen.getByRole('tab', {name: 'Leaderboard'});
        await userEvent.click(tabLearderboard);
        // Open the Upload Algorithm page when the Upload Algorithm button is pressed
        const submissionButton = screen.getByRole('button', {name: 'Upload Algorithm'});
        await userEvent.click(submissionButton);

        // Close the Upload Algorithm page when the CancelIcon button is pressed
        const cancelIcon = screen.getByTestId('CancelIcon')
        expect(cancelIcon).toBeTruthy();
        await userEvent.click(cancelIcon);
        expect(screen.cancelIcon).not.toBeTruthy();
    });

    it("Should upload algorithm", async () => {
        // Set up the mock function
        const mockOnChange = jest.fn();
        const mockFile = new File(['content'], 'mockfile.zip', {
            type: 'application/zip',
        });

        // Render the Analysis page and select teh Leader Board tab
        render(<div id="root"><Analysis/></div>, {wrapper: BrowserRouter});
        const tabLearderboard = screen.getByRole('tab', {name: 'Leaderboard'});
        await userEvent.click(tabLearderboard);

        // Test to upload the mockfile
        const fileInput = screen.getByLabelText("Upload");
        // screen.debug(nativeInput);
        await userEvent.upload(fileInput, mockFile);
        expect(mockOnChange).toHaveBeenCalledTimes(1);
    })
});

describe("Discussion", () => {
    it("Should show the discussion page when the tab was pressed", async () => {
        render(<div id="root"><Analysis/></div>, {wrapper: BrowserRouter});
         // Select and show the Discussion tub page
        const tabDiscussion = screen.getByRole('tab', {name: 'Discussion'});
        expect(tabDiscussion).toBeTruthy();
        await userEvent.click(tabDiscussion);
        expect(tabDiscussion).toHaveAttribute("aria-selected","true");
    });

    it("Should show the message when the Send/Edit/Update button was pressed", async () => {
        render(<div id="root"><Analysis/></div>, {wrapper: BrowserRouter});
        // Select the Discussion tub
        const tabDiscussion = screen.getByRole('tab', {name: 'Discussion'});
        await userEvent.click(tabDiscussion);

        // write down sample text to the textbox
        const textBox = screen.getAllByRole('textbox')[0];
        await userEvent.type(textBox, "test");

        // Click the send button and check if the sample text message was posted properlly
        const sendButton = screen.getAllByRole("button", {name: 'Send'})[0];
        await userEvent.click(sendButton);
        expect(screen.getByText("test")).toBeTruthy();

        // Check if the message can be editted by pressing Edit and Update button
        const editButton = screen.getAllByRole("button", {name: 'Edit'})[0];
        await userEvent.click(editButton);
        const updateBox = screen.getByText("test");
        await userEvent.type(updateBox, "abc");
        const updateButton = screen.getAllByRole("button", {name: 'Update'})[0];
        expect(updateButton).toBeTruthy();
        await userEvent.click(updateButton);
        expect(screen.getByText(/abc/i)).toBeTruthy();
    });
});