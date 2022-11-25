import { Box, Card, Stack, Typography, Avatar, Button } from "@mui/material";
import React, { useContext, useState } from "react";
import CommentContext from "./CommentContext";
import AddReply from "./AddReply";
import OwnReply from "./OwnReply";
import ReplyIcon from '@mui/icons-material/Reply';

const RepliesSection = ({ onReplies, onClicked, onTar }) => {
  const { IMGOBJ } = useContext(CommentContext);
  const [repliess, setReplies] = useState(onReplies);

  const addReply = (data) => {
    setReplies([
      ...repliess,
      {
        id: Math.floor(Math.random() * 10000),
        content: data,
        createdAt: "Just now",
        score: 0,
        replyingTo: `${onTar}`,
        replies: [],
        user: { username: "juliusomo" },
      },
    ]);
  };
  return (
    <Stack spacing={2} width="800px" alignSelf="flex-end">
      {repliess.map((rep) => {
        const { content, createdAt, score, user, replyingTo } = rep;
        const userName = user.username;
        const ava = IMGOBJ[`${userName}`];
        return userName === "juliusomo" ? (
          <OwnReply
            key={rep.id}
            comId={rep.id}
            onContent={content}
            onTime={createdAt}
            onCount={score}
            onTar={replyingTo}
          />
        ) : (
          <Card key={rep.id}>
            <Box sx={{ p: "15px" }}>
              <Stack spacing={2} direction="row">
                <Box sx={{ width: "100%" }}>
                  <Stack
                    spacing={2}
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Stack spacing={2} direction="row" alignItems="center">
                      <Avatar src={ava}></Avatar>
                      <Typography
                        fontWeight="bold"
                        sx={{ color: "neutral.darkBlue" }}
                      >
                        {userName}
                      </Typography>
                      <Typography sx={{ color: "neutral.grayishBlue" }}>
                        {createdAt}
                      </Typography>
                    </Stack>
                    <Button
                      variant="text"
                      sx={{
                        fontWeight: 500,
                        textTransform: "capitalize",
                        color: "custom.moderateBlue",
                      }}
                      startIcon={<ReplyIcon/>}
                    >
                      Reply
                    </Button>
                  </Stack>
                  <Typography
                    component="div"
                    sx={{ color: "neutral.grayishBlue", p: "20px 0" }}
                  >
                    <Typography
                      sx={{
                        color: "custom.moderateBlue",
                        width: "fit-content",
                        display: "inline-block",
                        fontWeight: 500,
                      }}
                    >
                      {`@${replyingTo}`}
                    </Typography>{" "}
                    {content}
                  </Typography>
                </Box>
              </Stack>
            </Box>
          </Card>
        );
      })}
      {onClicked && <AddReply onAdd={addReply} />}
    </Stack>
  );
};

export default RepliesSection;