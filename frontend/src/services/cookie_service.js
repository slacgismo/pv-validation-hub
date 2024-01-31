// This file should handle cookie logic for user sessions and private report authentication/access

import client from "./api_service";
import { useEffect, useState } from "react";
import Cookies from 'universal-cookie';

export const CookieService = {
    getUserCookie() {
        const cookies = new Cookies();
        return cookies.get('user');
    }
    /*
    setPrivateReportCookies(report_id, policy, signature, keyPairId) {
        const cookies = new Cookies();
        console.log("Setting cookies");
        cookies.set('CloudFront-Policy', 
            policy, 
            { path: "/", 
            secure: true });
        cookies.set('CloudFront-Signature', 
            signature, 
            { path: "/", 
            secure: true });
        cookies.set('CloudFront-Key-Pair-Id', 
            keyPairId, 
            { path: "/", 
            secure: true });

        console.log("Private Report Cookies set for user report " + report_id);

        return "Private Report Cookies set for user report " + report_id;
    }
    */
}