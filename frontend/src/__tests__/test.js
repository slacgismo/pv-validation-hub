// This file is used to run all the tests in the application
import AppTests from '../components/App/App.testsuite.js';
import DashboardTests from '../components/Analyses/Analyses.tests.js';
// import AnalysisTests from '../components/Analysis/Analysis.tests.js';

// This is the exported function that checks the main app page
AppTests();
DashboardTests();
// AnalysisTests();
