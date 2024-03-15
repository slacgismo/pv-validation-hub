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
import PropTypes from 'prop-types';
import CommentContext from './CommentContext.js';
import theme from './styles.jsx';
import RepliesSection from './RepliesSection.jsx';
import YouTag from './YouTag.jsx';

function Comment({ onPass }) {
  const cookies = new Cookies();
  const commentingUser = cookies.get('user');
  // stash id/score until we have a backend for this id, score
  const {
    content, createdAt, replies, user,
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
                        texttransform: 'capitalize',
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
                      texttransform: 'capitalize',
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
                      if (!commentText.trim()) {
                        console.log('If you want to remove the comment text, just delete the comment.');
                      } else {
                        setEditingComm(!editingComm);
                      }
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

Comment.propTypes = {
  onPass: PropTypes.shape({
    content: PropTypes.string.isRequired,
    createdAt: PropTypes.string.isRequired,
    replies: PropTypes.arrayOf(PropTypes.shape([])).isRequired,
    user: PropTypes.shape({
      username: PropTypes.string.isRequired,
    }).isRequired,
  }).isRequired,
};

export default Comment;
