import React, { useContext, useState } from 'react';
import {
  Avatar,
  Button,
  Card,
  Stack,
  Typography,
  ThemeProvider,
  TextField,
} from '@mui/material';
import Cookies from 'universal-cookie';
import { Box } from '@mui/system';
import { Edit } from '@mui/icons-material';
import ReplyIcon from '@mui/icons-material/Reply';
import CommentContext from './CommentContext.js';
import theme from './styles.jsx';
import RepliesSection from './RepliesSection.jsx';
import YouTag from './YouTag.jsx';

function Comment({ onPass }) {
  const cookies = new Cookies();
  const commentingUser = cookies.get('user');
  const {
    id, content, createdAt, score, replies, user,
  } = onPass;
  const { IMGOBJ } = useContext(CommentContext);
  const userName = user.username;
  const ava = IMGOBJ[`${userName}`];

  const [clicked, setClicked] = useState(false);
  const [editingComm, setEditingComm] = useState(false);
  const [commentText, setCommentText] = useState(content);

  return (
    <ThemeProvider theme={theme}>
      <Card>
        <Box sx={{ p: '15px' }}>
          <Stack spacing={2} direction="row">
            <Box sx={{ width: '100%' }}>
              <Stack
                spacing={2}
                direction="row"
                justifyContent="space-between"
                alignItems="center"
              >
                <Stack spacing={2} direction="row" alignItems="center">
                  <Avatar src={ava} />
                  <Typography
                    fontWeight="bold"
                    sx={{ color: 'neutral.darkBlue' }}
                  >
                    {userName}
                  </Typography>
                  {userName === commentingUser.username && <YouTag />}
                  <Typography sx={{ color: 'neutral.grayishBlue' }}>
                    {createdAt}
                  </Typography>
                </Stack>
                {userName === commentingUser.username ? (
                  <Stack direction="row" spacing={1}>
                    <Button
                      variant="text"
                      disabled={editingComm}
                      sx={{
                        fontWeight: 500,
                        textTransform: 'capitalize',
                        color: 'custom.moderateBlue',
                      }}
                      startIcon={<Edit />}
                      onClick={() => setEditingComm(!editingComm)}
                    >
                      Edit
                    </Button>
                  </Stack>
                ) : (
                  <Button
                    onClick={() => {
                      setClicked(!clicked);
                    }}
                    variant="text"
                    sx={{
                      fontWeight: 500,
                      textTransform: 'capitalize',
                      color: 'custom.moderateBlue',
                    }}
                    startIcon={<ReplyIcon />}
                  >
                    Reply
                  </Button>
                )}
              </Stack>
              {editingComm ? (
                <>
                  <TextField
                    sx={{ p: '20px 0' }}
                    multiline
                    fullWidth
                    minRows={4}
                    id="outlined-multilined"
                    placeholder="Don't leave this blank!"
                    value={commentText}
                    onChange={(e) => {
                      setCommentText(e.target.value);
                    }}
                  />
                  <Button
                    sx={{
                      float: 'right',
                      bgcolor: 'custom.moderateBlue',
                      color: 'neutral.white',
                      p: '8px 25px',
                      '&:hover': {
                        bgcolor: 'custom.lightGrayishBlue',
                      },
                    }}
                    onClick={() => {
                      !commentText.trim()
                        ? alert(
                          'If  you want to remove the comment text, just delete the comment.',
                        )
                        : setEditingComm(!editingComm);
                    }}
                  >
                    Update
                  </Button>
                </>
              ) : (
                <Typography sx={{ color: 'neutral.grayishBlue', p: '20px 0' }}>
                  {commentText}
                </Typography>
              )}
            </Box>
          </Stack>
        </Box>
      </Card>
      {replies && (
        <RepliesSection
          onReplies={replies}
          onClicked={clicked}
          onTar={userName}
        />
      )}
    </ThemeProvider>
  );
}
export default Comment;
