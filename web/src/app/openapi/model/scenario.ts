/**
 * PIN
 * Personal Intelligent Network
 *
 * The version of the OpenAPI document: 8.0.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { Frame } from './frame';
import { Event } from './event';


export interface Scenario { 
    _id?: string;
    _updated?: string;
    _created?: string;
    application: string;
    name?: string;
    description?: string;
    events?: Array<Event>;
    start?: string;
    end?: string;
    duration?: number;
    fps?: number;
    frames?: Array<Frame>;
}

