// This file should handle cookie logic for user sessions and private report authentication/access

import client from "./api_service";
import { useEffect, useState } from "react";
import Cookies from 'universal-cookie';

export const CookieService = {
    getUserCookie() {
        const cookies = new Cookies();
        return cookies.get('user');
    },
    setPrivateReportCookies(user_id, report_id, domainName, policy, signature, keyPairId) {
        const cookies = new Cookies();
        cookies.set('CloudFront-Policy', 
            policy, 
            { path: '/', 
            domain: domainName, 
            secure: true, 
            httpOnly: true });
        cookies.set('CloudFront-Signature', 
            signature, 
            { path: '/', 
            domain: domainName, 
            secure: true, 
            httpOnly: true });
        cookies.set('CloudFront-Key-Pair-Id', 
        keyPairId, 
        { path: '/', 
        domain: domainName, 
        secure: true, 
        httpOnly: true });

        return "Private Report Cookies set for user " + user_id + " and report " + report_id;
    }
}