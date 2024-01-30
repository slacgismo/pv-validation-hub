// This file should handle cookie logic for user sessions and private report authentication/access

import client from "./api_service";
import { useEffect, useState } from "react";
import Cookies from 'universal-cookie';

export const CookieService = {
    getUserCookie() {
        const cookies = new Cookies();
        return cookies.get('user');
    },
    setPrivateReportCookies(report_id, policy, signature, keyPairId) {
        const cookies = new Cookies();
        cookies.set('CloudFront-Policy', 
            policy, 
            { path: '/', 
            secure: true, 
            httpOnly: true });
        cookies.set('CloudFront-Signature', 
            signature, 
            { path: '/', 
            secure: true, 
            httpOnly: true });
        cookies.set('CloudFront-Key-Pair-Id', 
        keyPairId, 
        { path: '/', 
        secure: true, 
        httpOnly: true });

        return "Private Report Cookies set for user report " + report_id;
    }
}