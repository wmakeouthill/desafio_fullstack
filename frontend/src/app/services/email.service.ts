/**
 * Service para comunicação com a API de classificação de emails.
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
    ClassificacaoResultado,
    ClassificarEmailRequest,
    ClassificarArquivoResponse,
    ProvidersResponse,
    AIProvider
} from '../models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class EmailService {
    private readonly http = inject(HttpClient);
    private readonly apiUrl = `${environment.apiUrl}/emails`;

    /**
     * Lista os provedores de IA disponíveis.
     */
    getProviders(): Observable<ProvidersResponse> {
        return this.http.get<ProvidersResponse>(`${this.apiUrl}/providers`);
    }

    /**
     * Classifica um email a partir do texto.
     */
    classificarPorTexto(request: ClassificarEmailRequest): Observable<ClassificacaoResultado> {
        return this.http.post<ClassificacaoResultado>(
            `${this.apiUrl}/classificar`,
            request
        );
    }

    /**
     * Classifica um email a partir de um arquivo.
     */
    classificarPorArquivo(
        arquivo: File,
        provider?: AIProvider
    ): Observable<ClassificarArquivoResponse> {
        const formData = new FormData();
        formData.append('arquivo', arquivo);

        let params = new HttpParams();
        if (provider) {
            params = params.set('provider', provider);
        }

        return this.http.post<ClassificarArquivoResponse>(
            `${this.apiUrl}/classificar/arquivo`,
            formData,
            { params }
        );
    }
}
