import React, { useState } from 'react';
import { FormLabel, Grid, MenuItem } from '@mui/material';
import { REPORT_TYPES, REPORT_TYPE } from '../../constants/application-constant';
import Select from '@mui/material/Select';
import AnticipatedEAOSchedule from '../reports/eaReferral/anticipatedEAOSchedule';
import ResourceForecast from '../reports/resourceForecast/resourceForecast';
import ReportSample from '../reports/30-60-90Report/reportSample';

export default function ReportSelector() {
  const [selectedReport, setSelectedReport] = useState<string>('none');
  const reportTypeOptions = REPORT_TYPES
    .map((p, index) => (<MenuItem key={index + 1} value={p.Value}>{p.Text}</MenuItem>))
  return (
    <>
      <Grid container>
        <Grid item sm={2}>
          <FormLabel>Report</FormLabel>
        </Grid>
        <Grid item sm={5}>
          <Select value={selectedReport} onChange={(e: any) => setSelectedReport(e.target.value)}>
            <MenuItem key={0} value='none'>Select Report</MenuItem>
            {reportTypeOptions}
          </Select>
        </Grid>
      </Grid>
      {selectedReport === REPORT_TYPE.EA_REFERRAL && <AnticipatedEAOSchedule/>}
      {selectedReport === REPORT_TYPE.RESOURCE_FORECAST && <ResourceForecast/>}
      {selectedReport === REPORT_TYPE.REPORT_30_60_90 && <ReportSample/>}
    </>
  );
}