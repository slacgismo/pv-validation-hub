import { createContext, useState } from "react";
import { DashboardService } from "../../../services/dashboard_service";
import Cookies from 'universal-cookie';

const CommentContext = createContext();

export function CommentProvider({ children }) {

  const cookies = new Cookies();
  var comment_user = cookies.get("user");
  var data = DashboardService.getDiscussionComments("", comment_user.username);
  const [currentUser, comments] = [data.currentUser, data.comments];
  const [commentSection, setCommentSection] = useState(comments);
  const IMGOBJ = DashboardService.getImageObjects();
  const addComment = (data) => {
    setCommentSection([
      ...commentSection,
      {
        id: Math.floor(Math.random() * 10000),
        content: data,
        createdAt: "Just now",
        score: 0,
        replies: [],
        user: { username: comment_user.username },
      },
    ]);
  };
  return (
    <CommentContext.Provider
      value={{
        currentUser,
        commentSection,
        IMGOBJ,
        addComment
      }}
    >
      {children}
    </CommentContext.Provider>
  );
}

export default CommentContext;