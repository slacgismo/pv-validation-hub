import {
    Card,
    CardContent,
    Typography,
    Divider,
} from "@mui/material";

import React from "react";

function CardBar({ title, chart }) {
    return (
        <>
            <Card>
                <CardContent>
                    <Typography className={"cardbar123"} color="textPrimary">
                        {title}
                    </Typography>
                    <Divider />
                    {chart}
                </CardContent>
            </Card>
        </>
    );
}

export { CardBar };
