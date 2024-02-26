import React, { useContext } from 'react';
import { Container, Stack } from '@mui/material';
import Comment from './Comment.jsx';
import AddComment from './AddComment.jsx';
import CommentContext from './CommentContext.js';

export default function Discussion() {
  const { commentSection } = useContext(CommentContext);
  return (
    <Container maxWidth="md">
      <Stack spacing={3}>
        {commentSection.map((comment) => <Comment key={comment.id} onPass={comment} />)}
        <AddComment />
      </Stack>
    </Container>
  );
}
