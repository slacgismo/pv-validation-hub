import {
  Avatar,
  Button,
  Card,
  Stack,
  TextField,
  ThemeProvider,
} from "@mui/material";
import { Box } from "@mui/system";
import Cookies from 'universal-cookie';
import React, { useContext, useState } from "react";
import CommentContext from "./CommentContext";
import theme from "./styles";

const AddReply = ({ onAdd }) => {
  const cookies = new Cookies();
  let user = cookies.get("user");
  const { IMGOBJ } = useContext(CommentContext);
  const [replyText, setReplyText] = useState("");
  return (
    <ThemeProvider theme={theme}>
      <Card>
        <Box sx={{ p: "15px" }}>
          <Stack direction="row" spacing={2} alignItems="flex-start">
            <Avatar
              src={IMGOBJ[`${user.username}`]}
              variant="rounded"
              alt="user-avatar"
            />
            <TextField
              multiline
              fullWidth
              minRows={4}
              id="outlined-multilined"
              placeholder="Add a comment"
              value={replyText}
              onChange={(e) => {
                setReplyText(e.target.value);
              }}
            />
            <Button
              size="large"
              sx={{
                bgcolor: "custom.moderateBlue",
                color: "neutral.white",
                p: "8px 25px",
                "&:hover": {
                  bgcolor: "custom.lightGrayishBlue",
                },
              }}
              onClick={(e) => {
                !replyText.trim() ? e.preventDefault() : onAdd(replyText);
                setReplyText("");
              }}
            >
              Reply
            </Button>
          </Stack>
        </Box>
      </Card>
    </ThemeProvider>
  );
};

export default AddReply;